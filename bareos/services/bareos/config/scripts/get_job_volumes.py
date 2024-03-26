from dataclasses import dataclass
import json

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
               f'{volumes_str}\n])'


def load_json(file):
    with open(f'./{file}.json') as f:
        return json.load(f)['result'][file]


def main():
    volumes_json = load_json('volumes')
    jobsmedia_json = load_json('jobmedia')
    jobs_json = load_json('jobs')

    volumes = {}
    for vol in volumes_json:
        volumes[vol['mediaid']] = vol

    jobs = {}
    for j in jobs_json:
        jobs[j['jobid']] = j

    volumes_jobs: dict[str, list[str]] = {}
    jobs_with_vols = {}
    for jm in jobsmedia_json:
        jm_jobid = jm['jobid']
        jm_job = jobs[jm_jobid]

        if jm_jobid not in jobs_with_vols:
            jobs_with_vols[jm_jobid] = Job(jobid=jm_jobid, level=jm_job['level'],
                                           sched_time=jm_job['schedtime'], volumes=[])

        jm_mediaid = jm['mediaid']
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

    for job in jobs_list:
        print(job)




if __name__ == "__main__":
    main()

