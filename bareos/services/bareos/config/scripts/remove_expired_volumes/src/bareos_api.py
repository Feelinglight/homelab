from pathlib import Path
import subprocess
import json
import re

from src.utils import log_error, log_info


def run_subproccess(command: str) -> tuple[str, str]:
    command_print = command.replace('\n', ' \\n ')
    log_info(f'Запуск команды "{command_print}"')
    process = subprocess.Popen("bconsole", stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate(command.encode())
    stdout = stdout.decode()
    stderr = stderr.decode()
    return stdout, stderr


def run_bconsole_command(command: str):
    try:
        stdout, stderr = run_subproccess(f".api 2\n{command}")
        stdout = stdout.split('\n')
        stderr = stderr.split('\n')

        json_found = False
        output_command_idx = 0
        api_output_json = []

        for idx, line in enumerate(stdout):
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
        log_error(f"Не удалось выполнить команду {command} ({err})")
        raise


def get_resources_list(resource_type: str, filter_resource_type, filter_resource_value):
    result_json = run_bconsole_command(
        f'llist {resource_type} {filter_resource_type}={filter_resource_value}'
    )
    return result_json['result'][resource_type]


def get_jobs_list(job_name: str) -> list[dict[str, str]]:
    jobmedia_jobs_json = run_bconsole_command(f'llist job={job_name}')
    return jobmedia_jobs_json['result']['jobs']


def get_jobmedia_list(job_name: str) -> list[dict[str, str]]:
    jobmedia_jobs_json = run_bconsole_command(f'llist jobmedia job={job_name}')
    return jobmedia_jobs_json['result']['jobmedia']


def get_storage_device_name(storage):
    storage_resource_json = run_bconsole_command(f'show storage={storage}')
    storage_devices = storage_resource_json['result']['storages'][storage]['device']
    if len(storage_devices) != 1:
        raise ValueError(
            f'Error: В storage тома должен быть ровно 1 device (сейчас: [{storage_devices}])'
        )
    return storage_devices[0]


def get_volumes_folder(storage, device) -> Path:
    storage_status_command = f'status storage={storage}"'
    stdout, _ = run_subproccess(storage_status_command)
    result = re.search(rf'Device \"{device}\" \((.*)\)', stdout)
    if result is None:
        raise ValueError(
            f'Error: Не удалось найти Archive Device в выводе команды "{storage_status_command}"\n'
            f'Возможно нет связи с Storage Daemon'
        )
    return Path(result.group(1))


def delete_jobs(job_ids: list[int]) -> bool:
    job_ids_str: str = ','.join(map(str, job_ids))
    delete_result = run_bconsole_command(f'delete job jobid={job_ids_str}')
    if 'error' in delete_result:
        log_error(f'Не удалось удалить job-ы с id = "{job_ids_str}"')
        log_error(delete_result['error'])
        return False
    else:
        return True


def delete_volume(volume_name: str, pool: str) -> bool:
    delete_result = run_bconsole_command(f'delete volume={volume_name} pool={pool}')
    if 'error' in delete_result:
        log_error(f'Не удалось удалить volume с именем = "{volume_name}" (pool = "{pool}")')
        log_error(delete_result['error'])
        return False
    else:
        return True
