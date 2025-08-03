
BAREOS_STATUS = {
    "C": "Created, not yet running",
    "R": "Running",
    "B": "Blocked",
    "T": "Completed successfully",
    "E": "Terminated with errors",
    "e": "Non-fatal error",
    "f": "Fatal error",
    "D": "Verify found differences",
    "A": "Canceled by user",
    "I": "Incomplete job",
    "L": "Committing data",
    "W": "Terminated with warnings",
    "l": "Doing data despooling",
    "q": "Queued waiting for device",
    "F": "Waiting for Client",
    "S": "Waiting for Storage daemon",
    "m": "Waiting for new media",
    "M": "Waiting for media mount",
    "s": "Waiting for storage resource",
    "j": "Waiting for job resource",
    "c": "Waiting for client resource",
    "d": "Waiting on maximum jobs",
    "t": "Waiting on start time",
    "p": "Waiting on higher priority jobs",
    "i": "Doing batch insert file records",
    "a": "SD despooling attributes",
}

BSR_FILE_TEMPLATE = '{unique_jobid}-{jobid}-0-{job_level}.bsr'

LOG_FILE_TEMPLATE = '{job}-{jobid}-{job_level}.log'

