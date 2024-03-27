from dataclasses import dataclass

from src.utils import log_info, log_warning, log_error


@dataclass(kw_only=True)
class Volume:
    mediaid: int
    name: str


@dataclass(kw_only=True)
class Job:
    jobid: int
    sched_time: str
    level: str
    volumes: list[Volume]

    def __str__(self):
        volumes_str = '\n'.join([f'├─ {vol}' if (idx != len(self.volumes) - 1) else f'└─ {vol}'
                                 for idx, vol in enumerate(self.volumes)])
        return f'---> Job(jobid="{self.jobid}", sched_time="{self.sched_time}", ' \
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
            if j.level == "F":
                chains.append([j])
            else:
                chains[-1].append(j)

    return chains


def extract_chains(jobs_json: list[dict[str, str]], jobmedia_json: list[dict[str, str]]) -> \
        list[list[Job]]:
    jobs: dict[int, dict[str, str]] = {}
    for j in jobs_json:
        jobs[int(j['jobid'])] = j

    volumes_jobs: dict[int, list[int]] = {}
    jobs_with_vols: dict[int, Job] = {}
    for jm in jobmedia_json:
        jm_jobid: int = int(jm['jobid'])
        jm_job: dict[str, str] = jobs[jm_jobid]

        jm_mediaid = int(jm['mediaid'])
        jm_volumename = jm['volumename']

        if jm_mediaid not in volumes_jobs:
            volumes_jobs[jm_mediaid] = []
        volumes_jobs[jm_mediaid].append(jm_jobid)

        if len(volumes_jobs[jm_mediaid]) > 1:
            raise ValueError(f'Error: В томе "{jm_volumename}" mediaid = "{jm_mediaid}" '
                             f'записано несколько job (jobids = {volumes_jobs[jm_mediaid]})')

        if jm_jobid not in jobs_with_vols:
           jobs_with_vols[jm_jobid] = Job(jobid=jm_jobid, level=jm_job['level'],
                                           sched_time=jm_job['schedtime'], volumes=[])
        jobs_with_vols[jm_jobid].volumes.append(Volume(mediaid=jm_mediaid, name=jm_volumename))

    jobs_list = list(jobs_with_vols.values())
    for job in jobs_list:
        job.volumes.sort(key=lambda v: v.mediaid)
    jobs_list.sort(key=lambda j: j.jobid)

    chains = _find_job_chains(jobs_list)
    for idx, jobs_chain in enumerate(chains, start=1):
        log_info(f"Цепочка №{idx}:")
        for j in jobs_chain:
            job_vols = [v.name for v in j.volumes]
            log_info(f'{j.jobid} ({j.level}): {job_vols}')

    return chains


def delete_all_chains_except_last(job_chains: list[list[Job]], print_only: bool):
    if not job_chains:
        log_info(f"Ни одной цепочки job не найдено")
        return

    last_chains = job_chains[-1:]
    del job_chains[-1:]

    log_info(f"Цепочка, которая будет оставлена:\n"
             f"{[(j.jobid, j.level) for chain in last_chains for j in chain]}")
    log_info(f"Цепочки, которые будут удалены:\n"
             f"{[[(j.jobid, j.level) for j in chain] for chain in job_chains]}")

    if print_only:
        log_info("Скрипт запущен в режиме dry run. Тома не будут удалены")
    else:
        log_info("Удаление лишних томов...")

