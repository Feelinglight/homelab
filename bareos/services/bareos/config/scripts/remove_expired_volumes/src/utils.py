from typing import Any
import subprocess


def log_info(msg: Any):
    print(str(msg))


def log_warning(msg: Any):
    print(f"Warning: {msg}")


def log_error(msg: Any):
    print(f"Error: {msg}")

