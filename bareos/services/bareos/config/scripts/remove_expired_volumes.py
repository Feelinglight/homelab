from dataclasses import dataclass
from typing import Any
import subprocess
import argparse
import json
import re


def log_info(msg: Any):
    print(str(msg))

def log_warning(msg: Any):
    print(f"Warning: {msg}")

def log_error(msg: Any):
    print(f"Error: {msg}")


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


def bconsole_get_resources_list(resource_type: str, filter_resource_type, filter_resource_value):
    result_json = run_bconsole_command(
        f'llist {resource_type} {filter_resource_type}={filter_resource_value}'
    )
    return result_json['result'][resource_type]


@dataclass(kw_only=True)
class Volume:
    mediaid: str
    name: str


@dataclass(kw_only=True)
class Job:
    jobid: str
    sched_time: str
    level: str
    volumes: list[Volume]

    def __str__(self):
        volumes_str = '\n'.join([f'├─ {vol}' if (idx != len(self.volumes) - 1) else f'└─ {vol}'
                                 for idx, vol in enumerate(self.volumes)])
        return f'---------> Job(jobid="{self.jobid}", sched_time="{self.sched_time}", ' \
               f'level="{self.level}", ' \
               f'volumes = [\n' \
               f'{volumes_str}\n]'


def get_storage_device_name(storage):
    storage_resource_json = run_bconsole_command(f'show storage={storage}')
    storage_devices = storage_resource_json['result']['storages'][storage]['device']
    if len(storage_devices) != 1:
        raise ValueError(
            f'Error: В storage тома должен быть ровно 1 device (сейчас: [{storage_devices}])'
        )
    return storage_devices[0]


def get_device_folder(storage, device):
    storage_status_command = f'status storage={storage}"'
    stdout, _ = run_subproccess(storage_status_command)
    result = re.search(rf'Device \"{device}\" \((.*)\)', stdout)
    if result is None:
        raise ValueError(
            f'Error: Не удалось найти Archive Device в выводе команды "{storage_status_command}"'
        )
    return result.group(0)


def get_jobs_list(job_name: str):
    jobmedia_jobs_json = run_bconsole_command(f'llist job={job_name}')
    return jobmedia_jobs_json['result']['jobs']


def remove_expired_volumes(level: str, storage: str, job: str, dry_run: bool):
    if level != 'Full':
        log_info(f'При бэкапе с уровнем {level} тома не очищаются')
        return

    device = get_storage_device_name(storage)
    device_folder = get_device_folder(storage, device)
    log_info(f'Папка с томами для job = "{job}": "{device_folder}')

    jobs: list[Job] = []
    jobs_json = get_jobs_list(job)
    for job_json in jobs_json:
        job_id = job_json['jobid']
        volumes_list = bconsole_get_resources_list('volumes', 'jobid', job_id)
        volumes_list.sort(key=lambda v: v['mediaid'])

        jobs.append(
            Job(
                jobid=job_id,
                sched_time=job_json['schedtime'],
                level=job_json['level'],
                volumes=[Volume(mediaid=vol['mediaid'], name=vol['volumename'])
                         for vol in volumes_list]
            )
        )

    jobs.sort(key=lambda j: j.jobid)

    if jobs:
        for j in jobs:
            log_info(j)

    if not dry_run:
        pass


def main():
    parser = argparse.ArgumentParser(description="Example script with required arguments")
    parser.add_argument("-l", "--level", help="Specify the level", required=True)
    parser.add_argument("-s", "--storage", help="Specify the storage", required=True)
    parser.add_argument("-j", "--job", help="Specify the job", required=True)
    parser.add_argument("-d", "--dry-run", action='store_true')

    args = parser.parse_args()

    level: str = args.level
    storage: str = args.storage
    job: str = args.job
    dry_run: bool = args.dry_run or False

    log_info(f'Job: "{job}"; Level: "{level}"; Storage: "{storage}"')

    if level == "":
        log_error("Level (-l) - пустая строка")
        exit(1)

    if storage == "":
        log_error("Storage (-s) - пустая строка")
        exit(1)

    if job == "":
        log_error("Job (-j) - пустая строка")
        exit(1)

    remove_expired_volumes(level, storage, job, dry_run)


if __name__ == "__main__":
    log_info(f'Удаление лишних цепочек---------------------------------------')
    try:
        main()
    finally:
        log_info(f'Удаление лишних цепочек завершено-----------------------------')


