import logging
from logging.handlers import FileHandler
from pathlib import Path
from typing import Optional

logger = logging.getLogger('before-job')

class BareosWebuiFormatter(logging.Formatter):

    formats = {
        logging.DEBUG: "[D]",
        logging.INFO: "[I]",
        logging.WARNING: "[W] Warning:",
        logging.ERROR: "[E] Error:",
        logging.CRITICAL: "[C] Error:",
    }

    def format(self, record: logging.LogRecord) -> str:
        prefix = self.formats[record.levelno]
        if self._fmt is not None:
            return logging.Formatter(f'{prefix} {self._fmt}').format(record)
        return super().format(record)


def set_up_logging_stdout() -> None:
    stdout_log = logging.StreamHandler()
    stdout_log.setLevel(logging.INFO)
    stdout_log.setFormatter(BareosWebuiFormatter('%(message)s'))
    logger.addHandler(stdout_log)


def set_up_logging_file(log_path: Path):
    file_log = FileHandler(log_path)
    file_log.setLevel(logging.DEBUG)
    file_log.setFormatter('%(levelname)s | %(asctime)s: %(message)s')
    logger.addHandler(file_log)

