import traceback
import argparse

from src.utils import log_info, log_error
from src.bareos_api import get_storage_device_name, get_volumes_folder,\
    get_jobs_list, get_jobmedia_list
from src.bareos import delete_all_chains_except_last, extract_chains


def remove_expired_volumes(level: str, storage: str, pool: str, job: str, dry_run: bool) -> bool:
    """
    Удаляет все лишние цепочки бэкапов. Лишними считаются все цепочки до последней успешной цепочки.

    Функция должна вызываться в Job.RunBefore на стороне директора bareos. Если функция завершается
    с ошибкой, то бэкап должен быть отменен.

    В описании параметров в скобках указаны выражения bareos, с помощью которых можно получить
    значение параметра в Run Script (
    https://docs.bareos.org/Configuration/Director.html#character-substitution)

    :param level: Уровень Job, запущенной в данный момент (%l)
    :param storage: Storage Job, запущенной в данный момент (%w)
    :param pool: Pool Job, запущенной в данный момент (%p)
    :param job: Имя Job, запущенной в данный момент (%n)
    :param dry_run: Если True, то будут выведены только логи, с указанием ресурсов которые должны
        быть удалены. Физически ничего удалено не будет
    :return: True, если удаление завершилось успешно, False иначе
    """
    if level != 'Full':
        log_info(f'При бэкапе с уровнем {level} тома не очищаются')
        # dry_run = True
        return True


    jobs_json: list[dict[str, str]] = get_jobs_list(job)
    jobsmedia_json: list[dict[str, str]] = get_jobmedia_list(job)

    job_chains = extract_chains(jobs_json, jobsmedia_json)

    device = get_storage_device_name(storage)
    volumes_folder = get_volumes_folder(storage, device)
    log_info(f'Папка с томами для job = "{job}": "{volumes_folder}"')

    return delete_all_chains_except_last(job_chains, volumes_folder, pool, print_only=dry_run)


def main() -> None:
    parser = argparse.ArgumentParser(description="Example script with required arguments")
    parser.add_argument("-l", "--level", help="Specify the level", required=True)
    parser.add_argument("-s", "--storage", help="Specify the storage", required=True)
    parser.add_argument("-j", "--job", help="Specify the job", required=True)
    parser.add_argument("-p", "--pool", help="Specify the pool", required=True)
    parser.add_argument("-d", "--dry-run", help="Dry run", action='store_true')

    args = parser.parse_args()

    level: str = args.level
    storage: str = args.storage
    job: str = args.job
    pool: str = args.pool
    dry_run: bool = args.dry_run or False

    log_info(f'Job: "{job}"; Level: "{level}"; Storage: "{storage}"')

    if level == "":
        log_error("Level (-l) - пустая строка")
        exit(1)

    if level not in ("Full", "Incremental"):
        log_error(f"Скрипт рассчитан только на полные и инкрементальные бэкапы."
                  f"(текущий - {level})")
        exit(1)

    if storage == "":
        log_error("Storage (-s) - пустая строка")
        exit(1)

    if job == "":
        log_error("Job (-j) - пустая строка")
        exit(1)

    if job == "":
        log_error("Pool (-p) - пустая строка")
        exit(1)

    ok = remove_expired_volumes(level=level, storage=storage, pool=pool, job=job, dry_run=dry_run)
    if not ok:
        log_error('При удалении томов возникли ошибки')
        exit(1)


if __name__ == "__main__":
    log_info(f'Удаление лишних цепочек---------------------------------------')

    error = False
    try:
        main()
    except Exception as err:
        for line in traceback.format_exc().split('\n'):
            log_error(line)
        error = True

    log_info(f'Удаление лишних цепочек завершено-----------------------------')

    if error:
        exit(1)

