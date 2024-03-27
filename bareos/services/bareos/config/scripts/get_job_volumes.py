from dataclasses import dataclass
import json

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


def load_json(file):
    with open(f'./{file}.json') as f:
        return json.load(f)['result'][file]


def find_chains(jobs: list[Job]) -> list[list[Job]]:
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


def main():
    jobs_json = load_json('jobs')

    jobs: dict[int, dict[str, str]] = {}
    for j in jobs_json:
        jobs[int(j['jobid'])] = j

    jobsmedia_json = load_json('jobmedia')
    volumes_jobs: dict[int, list[int]] = {}
    jobs_with_vols: dict[int, Job] = {}
    for jm in jobsmedia_json:
        jm_jobid: int = int(jm['jobid'])
        jm_job: dict[str, str] = jobs[jm_jobid]

        if jm_jobid not in jobs_with_vols:
           jobs_with_vols[jm_jobid] = Job(jobid=jm_jobid, level=jm_job['level'],
                                           sched_time=jm_job['schedtime'], volumes=[])

        jm_mediaid = int(jm['mediaid'])
        jm_volumename = jm['volumename']

        if jm_mediaid not in volumes_jobs:
            volumes_jobs[jm_mediaid] = []

        volumes_jobs[jm_mediaid].append(jm_jobid)

        if len(volumes_jobs[jm_mediaid]) > 1:
            raise ValueError(f'Error: В томе "{jm_volumename}" mediaid = "{jm_mediaid}" '
                             f'записано несколько job (jobids = {volumes_jobs[jm_mediaid]})')

        jobs_with_vols[jm_jobid].volumes.append(Volume(mediaid=jm_mediaid, name=jm_volumename))

    jobs_list = list(jobs_with_vols.values())
    for job in jobs_list:
        job.volumes.sort(key=lambda v: v.mediaid)
    jobs_list.sort(key=lambda j: j.jobid)


    chains = find_chains(jobs_list)
    for idx, jobs_chain in enumerate(chains, start=1):
        print(f"---------> Chain №{idx}:")
        for job in jobs_chain:
            print(job)
    #     for j in jobs_chain:
    #         print(j)
    #         # job_vols = [v.name for v in j.volumes]
    #         # print(f'{j.jobid} ({j.level}): {job_vols}')



if __name__ == "__main__":
    main()

