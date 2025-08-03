import traceback
import argparse

from src.bareos_api import get_storage_device_name, get_volumes_folder,\
    get_jobs_list, get_jobmedia_list
from src.bareos import delete_all_chains_except_last, extract_chains
from src.logger import logger, set_up_logging_stdout, set_up_logging_file
from src import constants


def remove_expired_volumes(job: str, current_jobid: int, level: str, storage: str, pool: str,
                           dry_run: bool) -> bool:
    """
    Удаляет все лишние цепочки бэкапов. Лишними считаются все цепочки до последней успешной цепочки.

    Функция должна вызываться в Job.RunBefore на стороне директора bareos. Если функция завершается
    с ошибкой, то бэкап должен быть отменен.

    В описании параметров в скобках указаны выражения bareos, с помощью которых можно получить
    значение параметра в Run Script (
    https://docs.bareos.org/Configuration/Director.html#character-substitution)

    :param job: Имя Job, запущенной в данный момент (%n)
    :param current_jobid: Id Job, запущенной в данный момент (%n)
    :param level: Уровень Job, запущенной в данный момент (%l)
    :param storage: Storage Job, запущенной в данный момент (%w)
    :param pool: Pool Job, запущенной в данный момент (%p)
    :param dry_run: Если True, то будут выведены только логи, с указанием ресурсов которые должны
        быть удалены. Физически ничего удалено не будет
    :return: True, если удаление завершилось успешно, False иначе
    """
    if level != 'Full':
        logger.info(f'При бэкапе с уровнем {level} тома не очищаются')
        # dry_run = True
        return True

    jobs_json: list[dict[str, str]] = get_jobs_list(job)
    jobsmedia_json: list[dict[str, str]] = get_jobmedia_list(job)

    job_chains = extract_chains(current_jobid, jobs_json, jobsmedia_json)

    device = get_storage_device_name(storage)
    volumes_folder = get_volumes_folder(storage, device)

    # TODO: Сделать автоматическое удаление файлов логов
    set_up_logging_file(
        volumes_folder / constants.LOG_FILE_TEMPLATE.format(
            job=job, jobid=current_jobid, job_level=level
        )
    )
    logger.info(f'Папка с томами для job = "{job}": "{volumes_folder}"')
    logger.debug(f'Список job из bconsole:\n'
                 f'{jobs_json}\n\n\n')
    logger.debug(f'Список jobmedia из bconsole:\n'
                 f'{jobsmedia_json}\n\n\n')

    return delete_all_chains_except_last(job_chains, volumes_folder, pool, print_only=dry_run)


def main() -> None:
    parser = argparse.ArgumentParser(description="Example script with required arguments")
    parser.add_argument("-j", "--job", help="Specify the job", required=True)
    parser.add_argument("-i", "--jobid", help="Specify the jobid", required=True)
    parser.add_argument("-l", "--level", help="Specify the level", required=True)
    parser.add_argument("-s", "--storage", help="Specify the storage", required=True)
    parser.add_argument("-p", "--pool", help="Specify the pool", required=True)
    parser.add_argument("-d", "--dry-run", help="Dry run", action='store_true')

    args = parser.parse_args()

    job: str = args.job
    jobid: int = int(args.jobid)
    level: str = args.level
    storage: str = args.storage
    pool: str = args.pool
    dry_run: bool = args.dry_run or False

    logger.info(f'Job: "{job}"; Level: "{level}"; Storage: "{storage}"')

    if level == "":
        logger.error("Level (-l) - пустая строка")
        exit(1)

    if level not in ("Full", "Incremental"):
        logger.error(f"Скрипт рассчитан только на полные и инкрементальные бэкапы."
                  f"(текущий - {level})")
        exit(1)

    if storage == "":
        logger.error("Storage (-s) - пустая строка")
        exit(1)

    if job == "":
        logger.error("Job (-j) - пустая строка")
        exit(1)

    if job == "":
        logger.error("Pool (-p) - пустая строка")
        exit(1)

    ok = remove_expired_volumes(current_jobid=jobid, level=level, storage=storage, pool=pool,
                                job=job, dry_run=dry_run)
    if not ok:
        logger.error('При удалении томов возникли ошибки')
        exit(1)


if __name__ == "__main__":
    set_up_logging_stdout()
    logger.info(f'Удаление лишних цепочек---------------------------------------')

    error = False
    try:
        main()
    except Exception as err:
        for line in traceback.format_exc().split('\n'):
            logger.error(line)
        error = True

    logger.info(f'Удаление лишних цепочек завершено-----------------------------')

    if error:
        exit(1)

