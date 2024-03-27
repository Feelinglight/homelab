import json
import os

from src.bareos import extract_chains

script_dir = os.path.dirname(os.path.realpath(__file__))

def load_json(file):
    with open(f'{script_dir}/data/{file}.json') as f:
        return json.load(f)['result'][file]


def main():
    jobs_json = load_json('jobs')
    jobsmedia_json = load_json('jobmedia')
    job_chains = extract_chains(jobs_json, jobsmedia_json)



if __name__ == "__main__":
    main()

