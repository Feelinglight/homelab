from dataclasses import dataclass
from typing import NamedTuple
from pathlib import Path

from src.logger import logger
from src.bareos_api import delete_jobs, delete_volume
from src import constants


class Volume(NamedTuple):
    mediaid: int
    name: str


@dataclass(kw_only=True)
class Job:
    jobid: int
    name: str
    unique_id: str
    sched_time: str
    level: str
    """ Должно быть "F" (Full) или "I" (Incremental)"""
    is_ok: bool
    status: str
    volumes: list[Volume]

    def bsr_name(self) -> str:
        """
        :return: Имя bootstrap-файла для этой Job. Должно совпадать с полем Write Bootstrap в
            ресурсе Job. (Синхронизируется вручную для всех Job)
        """
        job_level = "Full" if self.level == "F" else "Incremental"
        # TODO: Брать шаблон bsr файла из ресурса Job автоматически
        return constants.BSR_FILE_TEMPLATE.format(
            unique_jobid=self.unique_id, jobid=self.jobid, job_level=job_level
        )

    def log_name(self) -> str:
        """
        :return: Имя log-файла этого скрипта для этой Job
        """
        return constants.LOG_FILE_TEMPLATE.format(
            job=self.name, jobid=self.jobid, job_level=self.level
        )

    def __str__(self):
        volumes_str = '\n'.join([f'├─ {vol}' if (idx != len(self.volumes) - 1) else f'└─ {vol}'
                                 for idx, vol in enumerate(self.volumes)])
        return f'---> Job(jobid="{self.jobid}", ' \
               f'name="{self.name}", ' \
               f'unique_id="{self.unique_id}", ' \
               f'sched_time="{self.sched_time}", ' \
               f'level="{self.level}", ' \
               f'volumes = [\n' \
               f'{volumes_str}\n])'


def _find_job_chains(jobs: list[Job]) -> list[list[Job]]:
    """
    Ищет в отсортированном списке job цепочки бэкапов.

    :return: Список цепочек бэкапов
    """
    assert sorted(jobs, key=lambda j: j.sched_time) == jobs, \
        f"Полученные из bareos job-ы не отсортированы: {jobs}"

    chains: list[list[Job]] = []
    for j in jobs:
        if j.level == "F" or len(chains) == 0:
            chains.append([j])
        else:
            chains[-1].append(j)

    return chains


def extract_chains(current_jobid: int, jobs_json: list[dict[str, str]],
                   jobmedias_json: list[dict[str, str]]) \
        -> list[list[Job]]:
    """
    Извлекает из списков jobs_json и jobmedias_json цепочки бэкапов, влючая тома, в которых эти
    бэкапы хранятся.

    Цепочкой считается полный бэкап и любое количество последующих за ним бэкапов с
    другими уровнями (не полными).

    :param current_jobid: Id job-ы, запущенной в данный момент
    :param jobs_json: Список бэкапов, полученный из команды bconsole llist job=...
    :param jobmedias_json: Список jobmedia, полученный из команды bconsole llist jobmedia job=...
    :return: Список цепочек Job, отсортированный по времени
    """
    jobs: list[Job] = []
    for job_json in jobs_json:
        assert job_json['name'] == jobs_json[0]['name'], \
            f'В jobs_json присутствуют бэкапы от разных Job:' \
            f'{job_json["name"] != jobs_json[0]["name"]}'
        assert job_json['level'] in ('F', 'I'), \
            'Все бэкапы должны быть полными, либо инкрементальными'

        jobid = job_json['jobid']
        if int(jobid) == current_jobid:
            continue

        # Найти все jobmedia для jobid
        jobmedias: list[dict[str, str]] = []
        for jm in jobmedias_json:
            if jm['jobid'] == jobid:
                jobmedias.append(jm)

        job_volumes: set[Volume] = set()
        for jm in jobmedias:
            job_volumes.add(Volume(mediaid=int(jm['mediaid']), name=jm['volumename']))

        # https://docs.bareos.org/Appendix/CatalogTables.html#index-3
        job_ok = True if job_json['jobstatus'] in ('T', 'e', 'W') else False
        jobs.append(
            Job(jobid=int(jobid), name=job_json['name'], unique_id=job_json['job'],
                level=job_json['level'], sched_time=job_json['schedtime'], is_ok=job_ok,
                status=constants.BAREOS_STATUS[job_json['jobstatus']],
                volumes=sorted(list(job_volumes), key=lambda v: v.mediaid))
        )
    jobs.sort(key=lambda j: j.jobid)

    # TODO: Добавить проверку, что в одном томе записана только одна job
    # assert ???, f'В томе "{jm_volumename}" mediaid = "{jm_mediaid}" '
    #             f'записано несколько job (jobids = {volumes_jobs[jm_mediaid]})')

    # TODO: Добавить проверку, что все тома в папке томов относятся к какой-то из существующих job

    chains = _find_job_chains(jobs)
    for idx, jobs_chain in enumerate(chains, start=1):
        job_status = 'successed' if jobs_chain[0].is_ok else 'failed'
        logger.info(f'Цепочка №{idx} ({job_status}: {jobs_chain[0].status}):')
        for j in jobs_chain:
            logger.info(f'Job: {j.jobid} ({j.level})')
            job_vols = [v.name for v in j.volumes]
            logger.debug(f'Volumes: {job_vols}')

    return chains


def _separate_chains_to_remove(job_chains: list[list[Job]]) -> \
        tuple[list[list[Job]], list[list[Job]]]:
    """
    Разделяет все цепочки на 2 списка: те, которые нужно удалить и те, которые нужно оставить.

    Сначала ищется последняя успешная цепочка, т. е. та, в которой Full бэкап успешный.
    Все цепочки после успешной цепочки оставляются. Все цепочки до успешной цепочки удаляются.

    :param job_chains: Список цепочек, отсортированный по времени
    :return: Кортеж (список цепочек, которые нужно оставить; список цепочек, которые нужно удалить)
    """
    success_chain_idx = 0
    for idx, chain in enumerate(reversed(job_chains)):
        assert len(chain) != 0

        if chain[0].is_ok:
            success_chain_idx = len(job_chains) - idx - 1
            logger.info(f'Последняя успешная цепочка - №{success_chain_idx + 1}')
            break

    chains_to_leave = job_chains[success_chain_idx:]
    chains_to_remove = job_chains[:success_chain_idx]

    logger.info(f"Цепочки, которые будут оставлены:\n"
             f"{[[(j.jobid, j.level) for j in chain] for chain in chains_to_leave]}")
    logger.info(f"Цепочки, которые будут удалены:\n"
             f"{[[(j.jobid, j.level) for j in chain] for chain in chains_to_remove]}")

    return chains_to_leave, chains_to_remove


def _get_volume_files_of_jobs(jobs: list[Job], volumes_folder: Path, failed_only: bool) \
        -> list[Path]:
    """
    :param jobs: Список бэкапов, файлы томов которых нужно вернуть.
    :param volumes_folder: Папка пула, к которому относится том (Archive Type девайса пула).
    :param failed_only: Если True, то будут возвращены только файлы проваленных бэкапов.
    :return: Список файлов томов всех бэкапов (jobs)
    """
    jobs_ = jobs if not failed_only else [j for j in jobs if not j.is_ok]

    files = []
    for job in jobs_:
        for vol in job.volumes:
            volume_path = volumes_folder / vol.name
            if volume_path.is_file():
                files.append(volume_path)
            elif job.is_ok:
                # Для заваленных job нормально отсутствие файлов томов, логируем только для успешных
                logger.warning(f'Файл тома "{volume_path} "'
                               f'(jobid = {job.jobid}, mediaid={vol.mediaid}) не найден')

    return files


def _get_bsr_files_of_jobs(jobs: list[Job], volumes_folder: Path) -> list[Path]:
    """
    :param jobs: Список бэкапов, bsr файлы которых нужно вернуть.
    :param volumes_folder: Папка пула, к которому относятся тома бэкапов
        (Archive Type девайса пула).
    :return: Список bsr файлов всех бэкапов (jobs)
    """
    files = []
    for job in jobs:
        bsr_path = volumes_folder / job.bsr_name()
        if bsr_path.is_file():
            files.append(bsr_path)
        elif job.is_ok:
            logger.debug(f'Bsr файл "{bsr_path}" (jobid = {job.jobid}) не найден')

    return files


def _get_log_files_of_jobs(jobs: list[Job], volumes_folder: Path) -> list[Path]:
    """
    :param jobs: Список бэкапов, log-файлы которых нужно вернуть.
    :param volumes_folder: Папка пула, к которому относятся тома бэкапов
        (Archive Type девайса пула).
    :return: Список log файлов всех бэкапов (jobs)
    """
    files = []
    for job in jobs:
        log_name = volumes_folder / job.log_name()
        if log_name.is_file():
            files.append(log_name)
        elif job.is_ok:
            logger.debug(f'Log файл "{log_name}" (jobid = {job.jobid}) не найден')

    return files


def _remove_job_chains(job_chains: list[list[Job]], volumes_pool: str, job_files: list[Path]) -> bool:
    ok = True
    for path in job_files:
        try:
            logger.debug(f'Удаление файла "{path}" ...')
            path.unlink()
        except FileNotFoundError as err:
            logger.error(f'Не удалось удалить файл "{path}"\nОшибка: {err}')
            ok = False

    job_delete_success = delete_jobs(
        [j.jobid for chain in job_chains for j in chain]
    )
    if not job_delete_success:
        ok = False

    for chain in job_chains:
        for job in chain:
            for v in job.volumes:
                volume_delete_success = delete_volume(v.name, volumes_pool)
                if not volume_delete_success:
                    ok = False
    return ok


def delete_all_chains_except_last(job_chains: list[list[Job]], volumes_folder: Path,
                                  volumes_pool: str, print_only: bool) -> bool:
    """
    Удаляет все цепочки бэкапов которые выполнены перед последней успешной цепочкой.
    Функцию нужно вызывать прямо перед выполнением следующего полного бэкапа.

    Также удаляет файлы томов всех неудачных бэкапов. В БД bareos все неудачные бэкапы и их тома
    оставляются. Бэкапы оставляются на всякий случай (например, чтобы иметь возможность смотреть их
    логи). Тома оставляются потому, что если удалить хотя бы один том бэкапа, то bareos удалит
    вместе с ним сам бэкап.

    :param job_chains: Цепочки бэкапов, извлекаются из bareos с помощью функции extract_chains.
    :param volumes_folder: Папка в которой должны лежать все тома всех цепочек.
    :param volumes_pool: Пул, которому должны принадлежать все тома всех цепочек.
    :param print_only: Если True, то функция не будет ничего удалять физически, а только проверит
        цепочки на наличие ошибок
    :return: True, если удаление прошло без ошибок, иначе False
    """
    if not job_chains:
        logger.info(f"Ни одной цепочки job не найдено")
        return True

    chains_to_leave, chains_to_remove = _separate_chains_to_remove(job_chains)

    if len(job_chains) != 0:
        assert len(chains_to_leave) > 0, f'{len(chains_to_leave)} == 0'
        assert chains_to_leave[0][0].level == 'F', str(chains_to_leave[0][0])
        assert chains_to_leave[0][0].is_ok or all(not c[0].is_ok for c in chains_to_leave), \
            str(chains_to_leave[0][0])
        assert len(chains_to_leave) + len(chains_to_remove) == len(job_chains), \
            f'{len(chains_to_leave)} + {len(chains_to_remove)} != {len(job_chains)}'

    files_to_delete: list[Path] = []

    logger.debug(f'Сбор файлов цепочек, которые будут оставлены')
    # Файлы собираются заранее, чтобы видеть логи даже в print_only = True
    for chain in chains_to_leave:
        logger.debug(chain)
        # Удаляем только файлы, если удалить том в bareos, то он автоматически удалит job
        files_of_failed_jobs = _get_volume_files_of_jobs(chain, volumes_folder, failed_only=True)
        files_to_delete.extend(files_of_failed_jobs)

    logger.debug(f'Сбор файлов цепочек, которые будут удалены')
    for chain in chains_to_remove:
        logger.debug(chain)
        bsr_files = _get_bsr_files_of_jobs(chain, volumes_folder)
        files_to_delete.extend(bsr_files)

        log_files = _get_log_files_of_jobs(chain, volumes_folder)
        files_to_delete.extend(log_files)

        volume_files = _get_volume_files_of_jobs(chain, volumes_folder, failed_only=False)
        files_to_delete.extend(volume_files)

    if not print_only:
        return _remove_job_chains(chains_to_remove, volumes_pool, files_to_delete)
    else:
        logger.info("Скрипт запущен в режиме dry run. Тома не будут удалены")
        return True

