from pathlib import Path
from typing import Any
import subprocess
import json
import re

from src.logger import logger


def _run_bconsole_subproccess(command: str) -> tuple[str, str]:
    """
    Запускает команду в bconsole.
    Возможные команды: https://docs.bareos.org/TasksAndConcepts/BareosConsole.html

    :param command: Команда для bconsole - произвольная строка.
    :return: Кортеж (stdout, stderr) процесса bconsole
    """
    command_print = command.replace('\n', ' \\n ')
    logger.debug(f'Запуск команды "{command_print}"')
    process = subprocess.Popen("bconsole", stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate(command.encode())
    stdout_str = stdout.decode()
    stderr_str = stderr.decode()
    return stdout_str, stderr_str


def run_bconsole_command(command: str) -> dict[str, Any]:
    """
    Запускает команду bconsole в режиме json api.
    Примеры вывода команд в режиме json api:
    https://docs.bareos.org/DeveloperGuide/api.html#api-mode-2-json

    При ошибках выполнения команды бросает исключение.

    :param command: Команда для bconsole - произвольная строка.
    :return: json-словарь с результатом выполнения команды
    """
    try:
        stdout_str, stderr_str = _run_bconsole_subproccess(f".api 2\n{command}")
        stdout = stdout_str.split('\n')
        stderr = stderr_str.split('\n')

        json_found = False
        output_command_idx = 0
        api_output_json = []

        for idx, line in enumerate(stdout):
            # Ищем вывод команды .api 2, его возвращать не надо, только проверить на ошибки
            if line == '.api 2':
                json_found = True

            elif json_found:
                if line == f"}}{command}{{":
                    api_output_json.append('}')
                    output_command_idx = idx
                    break

                api_output_json.append(line)

        command_output_json = ['{']
        for line in stdout[output_command_idx + 1:]:
            command_output_json.append(line)

        api_output = json.loads("\n".join(api_output_json))

        jsonrpc_supported_version = '2.0'
        if api_output['jsonrpc'] != jsonrpc_supported_version:
            raise NotImplementedError(
                f'Error: Скрипт написан для версии jsonrpc={jsonrpc_supported_version}'
            )
        elif 'error' in api_output:
            raise ValueError(api_output)

        command_output = json.loads("\n".join(command_output_json))

        return command_output
    except Exception as err:
        logger.error(f"Не удалось выполнить команду {command} ({err})")
        raise


def get_resources_list(resource_type: str, filter_resource_type: str,
                       filter_resource_value: str) -> \
        list[dict[str, str]]:
    """
    Функция для вызова однотипных команд llist bconsole. Примеры таких команд

    - llist volume pool=some_pool
    - llist jobmedia job=some_job
    - и т. д.

    Подробнее про команды list и llist:
    https://docs.bareos.org/TasksAndConcepts/BareosConsole.html#id26

    Примерные поля, которые возвращают команды list и llist для различных ресурсов:
    https://docs.bareos.org/DeveloperGuide/catalog.html. Реально полей может быть больше, но
    все перечисленные в документации присутствуют. Там же приведена uml-диаграмма БД bareos.

    :param resource_type: Тип ресурса, список которых нужно получить (volume, jobmedia, ...)
    :param filter_resource_type: Тип ресурса фильтра (jobid, pool, volume, ...)
    :param filter_resource_value: Значение ресурса фильтра
    :return: Список ресурсов в формате json
    """
    result_json = run_bconsole_command(
        f'llist {resource_type} {filter_resource_type}={filter_resource_value}'
    )
    return result_json['result'][resource_type]


def get_jobs_list(job_name: str) -> list[dict[str, str]]:
    """
    Возвращает список экземпляров Job с именем job_name. Подробности про llist в
    документации к функции get_resources_list.

    :param job_name: Имя Job, для которой нужно получить все экземпляры
    :return: Список job в формате json
    """
    jobmedia_jobs_json = run_bconsole_command(f'llist job={job_name}')
    return jobmedia_jobs_json['result']['jobs']


def get_jobmedia_list(job_name: str) -> list[dict[str, str]]:
    """
    Возвращает список JobMedia для Job-ы с именем job_name. Подробности про llist в
    документации к функции get_resources_list.

    :param job_name: Имя Job, для которой нужно получить все экземпляры JobMedia
    :return: Список JobMedia в формате json
    """
    jobmedia_jobs_json = run_bconsole_command(f'llist jobmedia job={job_name}')
    return jobmedia_jobs_json['result']['jobmedia']


def get_storage_device_name(storage_name: str) -> str:
    """
    Возвращает имя ресурса Device для Storage с именем storage_name

    :param storage_name: Имя Storage, для которого нужно получить имя Device
    :return: Имя ресурса Device
    """
    storage_resource_json = run_bconsole_command(f'show storage={storage_name}')
    storage_devices = storage_resource_json['result']['storages'][storage_name]['device']
    if len(storage_devices) != 1:
        raise ValueError(
            f'Error: В storage тома должен быть ровно 1 device (сейчас: [{storage_devices}])'
        )
    return storage_devices[0]


def get_volumes_folder(storage_name: str, device_name: str) -> Path:
    """
    Возвращает Archive Type для Device с именем device_name. В этой программе подразумевается,
    что это всегда путь к папке, в которой хранятся тома Storage с именем storage_name.

    Делается не очень легальным способом, с помощью парсинга команды status storage (которая
    вообще не работает в режиме json api), потому что в bconsole нет нормального способа получить
    Archive Type устройства.

    Пример вывода команды status storage:
    https://docs.bareos.org/TasksAndConcepts/BareosConsole.html#id46

    :param storage_name: Имя Storage, в котором должен находиться Device с именем device_name
    :param device_name: Имя Device, для которого нужно получить Archive Type
    :return: Путь к папке с файлами томов (Archive Type устройства device_name)
    """
    storage_status_command = f'status storage={storage_name}"'
    stdout, _ = _run_bconsole_subproccess(storage_status_command)
    result = re.search(rf'Device \"{device_name}\" \((.*)\)', stdout)
    if result is None:
        raise ValueError(
            f'Error: Не удалось найти Archive Device в выводе команды "{storage_status_command}"\n'
            f'Возможно нет связи с Storage Daemon'
        )
    return Path(result.group(1))


def delete_jobs(job_ids: list[int]) -> bool:
    """
    Удаляет из БД bareos Job-ы с id перечисленными в job_ids.

    :param job_ids: Id Job, которые нужно удалить
    :return: True, если команда удаления завершилась без ошибок, иначе False
    """
    if not job_ids:
        return True

    job_ids_str: str = ','.join(map(str, job_ids))
    delete_result = run_bconsole_command(f'delete job jobid={job_ids_str}')
    if 'error' in delete_result:
        logger.error(f'Не удалось удалить job-ы с id = "{job_ids_str}"')
        logger.error(delete_result['error'])
        return False
    else:
        return True


def delete_volume(volume_name: str, pool: str) -> bool:
    """
    Удаляет из БД bareos том в пуле pool с именем volume_name.

    :param volume_name: Имя тома
    :param pool: Пул, в котором находится том
    :return: True, если команда удаления завершилась без ошибок, иначе False
    """
    delete_result = run_bconsole_command(f'delete volume={volume_name} pool={pool}')
    if 'error' in delete_result:
        logger.error(f'Не удалось удалить volume с именем = "{volume_name}" (pool = "{pool}")')
        logger.error(delete_result['error'])
        return False
    else:
        return True
