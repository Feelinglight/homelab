from dataclasses import dataclass
from typing import Optional
from pathlib import Path

from src.utils import log_info, log_warning, log_error
from src.bareos_api import delete_jobs, delete_volume


@dataclass(kw_only=True)
class Volume:
    mediaid: int
    name: str


@dataclass(kw_only=True)
class Job:
    jobid: int
    unique_id: str
    sched_time: str
    level: str
    # Заменить на succeded, потому что failed сейчас это не правильно
    failed: bool
    volumes: list[Volume]

    def bsr_name(self) -> str:
        job_level = "Full" if self.level == "F" else "Incremental"
        return f'{self.unique_id}-{self.jobid}-0-{job_level}.bsr'

    def __str__(self):
        volumes_str = '\n'.join([f'├─ {vol}' if (idx != len(self.volumes) - 1) else f'└─ {vol}'
                                 for idx, vol in enumerate(self.volumes)])
        return f'---> Job(jobid="{self.jobid}", ' \
               f'unique_id="{self.unique_id}", ' \
               f'sched_time="{self.sched_time}", ' \
               f'level="{self.level}", ' \
               f'volumes = [\n' \
               f'{volumes_str}\n])'


def _find_job_chains(jobs: list[Job]) -> list[list[Job]]:
    """
    Ищет в отсортированном списке job цепочки бэкапов Full-Increment
    Возвращает цепочки, отсортированные по времени
    """
    assert sorted(jobs, key=lambda j: j.sched_time) == jobs, \
        f"Полученные из bareos job-ы не отсортированы: {jobs}"

    chains: list[list[Job]] = []
    if len(jobs) != 0:
        for j in jobs:
            if j.level == "F" or len(chains) == 0:
                chains.append([j])
            else:
                chains[-1].append(j)

    return chains


def extract_chains(jobs_json: list[dict[str, str]], jobmedias_json: list[dict[str, str]]) -> \
        list[list[Job]]:
    jobs: list[Job] = []
    for job_json in jobs_json:
        jobid = job_json['jobid']
        # Найти все jobmedia для jobid
        jobmedias: list[dict[str, str]] = []
        for jm in jobmedias_json:
            if jm['jobid'] == jobid:
                jobmedias.append(jm)

        # Создать Job, Volumes
        job_volumes: list[Volume] = []
        for jm in jobmedias:
            job_volumes.append(Volume(mediaid=int(jm['mediaid']), name=jm['volumename']))
        job_volumes.sort(key=lambda v: v.mediaid)

        # https://docs.bareos.org/Appendix/CatalogTables.html#index-3
        job_failed = False if job_json['jobstatus'] in ('T', 'e') else True
        jobs.append(
            Job(jobid=int(jobid), unique_id=job_json['job'], level=job_json['level'],
                sched_time=job_json['schedtime'], failed=job_failed, volumes=job_volumes)
        )
    jobs.sort(key=lambda j: j.jobid)

    # TODO: Добавить проверку, что в одном томе записана только одна job
    # raise ValueError(f'Error: В томе "{jm_volumename}" mediaid = "{jm_mediaid}" '
                     # f'записано несколько job (jobids = {volumes_jobs[jm_mediaid]})')

    chains = _find_job_chains(jobs)
    for idx, jobs_chain in enumerate(chains, start=1):
        job_status = 'failed' if jobs_chain[0].failed else 'successed'
        log_info(f"Цепочка №{idx} ({job_status}):")
        for j in jobs_chain:
            job_vols = [v.name for v in j.volumes]
            log_info(f'{j.jobid} ({j.level}): {job_vols}')

    return chains


def _separate_chains_to_remove(job_chains: list[list[Job]]) -> \
    tuple[list[list[Job]], list[list[Job]]]:
    """
    Разделяет все цепочки на 2 списка: те, которые нужно удалить и те, которые нужно оставить.

    Сначала ищется последняя успешная цепочка, т. е. та, в которой Full бэкап успешный.
    Все цепочки после успешной цепочки оставляются. Все цепочки до успешной цепочки удаляются.
    """

    success_chain_idx = 0
    for idx, chain in enumerate(reversed(job_chains)):
        assert len(chain) != 0

        if not chain[0].failed:
            success_chain_idx = len(job_chains) - idx - 1
            log_info(f'Последняя успешная цепочка - №{success_chain_idx + 1}')
            break

    return job_chains[success_chain_idx:], job_chains[:success_chain_idx]


def get_volume_path(jobid: int, volume: Volume, volumes_folder: Path) -> Optional[Path]:
    volume_path = volumes_folder / volume.name
    if volume_path.is_file():
        return volume_path
    else:
        log_error(f'Файл тома "{volume_path} "'
                    f'(jobid = {jobid}, mediaid={volume.mediaid}) не найден')


def _get_volume_files_of_jobs(jobs: list[Job], volumes_folder: Path, failed_only: bool) \
        -> list[Path]:
    jobs_ = jobs if not failed_only else [j for j in jobs if j.failed]

    files = []
    for job in jobs_:
        for vol in job.volumes:
            volume_path = get_volume_path(job.jobid, vol, volumes_folder)
            if volume_path is not None:
                files.append(volume_path)

    return files


def _get_bsr_files_of_jobs(jobs: list[Job], volumes_folder: Path) -> list[Path]:
    files = []
    for job in jobs:
        bsr_path = volumes_folder / job.bsr_name()
        if bsr_path.is_file():
            files.append(bsr_path)
        elif not job.failed:
            log_error(f'Bsr файл "{bsr_path}" (jobid = {job.jobid}) не найден')

    return files


def delete_all_chains_except_last(job_chains: list[list[Job]], volumes_folder: Path,
                                  volumes_pool: str, print_only: bool):
    if not job_chains:
        log_info(f"Ни одной цепочки job не найдено")
        return

    chains_to_leave, chains_to_remove = _separate_chains_to_remove(job_chains)

    log_info(f"Цепочки, которые будут оставлены:\n"
             f"{[[(j.jobid, j.level) for j in chain] for chain in chains_to_leave]}")
    log_info(f"Цепочки, которые будут удалены:\n"
             f"{[[(j.jobid, j.level) for j in chain] for chain in chains_to_remove]}")

    if len(job_chains) != 0:
        assert len(chains_to_leave) > 0, f'{len(chains_to_leave)} == 0'
        assert chains_to_leave[0][0].level == 'F', str(chains_to_leave[0][0])
        assert not chains_to_leave[0][0].failed, str(chains_to_leave[0][0])
        assert len(chains_to_leave) + len(chains_to_remove) == len(job_chains), \
            f'{len(chains_to_leave)} + {len(chains_to_remove)} != {len(job_chains)}'

    files_to_delete: list[Path] = []

    # Файлы собираются заранее, чтобы видеть логи даже в print_only = True
    for chain in chains_to_leave:
        # Удаляем только файлы, если удалить том в bareos, то он автоматически удалит job
        files_of_failed_jobs = _get_volume_files_of_jobs(chain, volumes_folder, failed_only=True)
        files_to_delete.extend(files_of_failed_jobs)

    for chain in chains_to_remove:
        bsr_files = _get_bsr_files_of_jobs(chain, volumes_folder)
        files_to_delete.extend(bsr_files)

        volume_files = _get_volume_files_of_jobs(chain, volumes_folder, failed_only=False)
        files_to_delete.extend(volume_files)

    if not print_only:
        error = False

        for path in files_to_delete:
            try:
                path.unlink()
            except FileNotFoundError as err:
                log_error(f'Не удалось удалить файл "{path}"\nОшибка: {err}')
                error = True

        job_delete_success = delete_jobs(
            [j.jobid for chain in chains_to_remove for j in chain ]
        )
        if not job_delete_success:
            error = True

        for chain in chains_to_remove:
            for job in chain:
                for v in job.volumes:
                    volume_delete_success = delete_volume(v.name, volumes_pool)
                    if not volume_delete_success:
                        error = True

        if error:
            log_error('При удалении томов возникли ошибки')
            exit(1)
    else:
        log_info("Скрипт запущен в режиме dry run. Тома не будут удалены")

