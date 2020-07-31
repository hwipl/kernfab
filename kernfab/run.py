"""
Module for running commands
"""

import time

import invoke                   # type: ignore
from fabric import Connection   # type: ignore

from kernfab import config


def _run_cmd(host: str, cmd: str, hide=False) -> invoke.runners.Result:
    """
    Helper for running commands
    """

    cmd = f"{config.BASH_TOOL} -l -c \"{cmd}\""
    if host == "":
        result = invoke.run(cmd, warn=True, hide=hide)
    else:
        conn = Connection(host)
        result = conn.run(cmd, warn=True, hide=hide)
    return result


def run_cmd(host: str, cmd: str) -> str:
    """
    Run a command
    """

    result = _run_cmd(host, cmd)
    return result.stdout


def run_try(host: str, cmd: str, timeout: int) -> str:
    """
    Try to run a command multiple times until it is successful for a maximum of
    timeout seconds
    """

    start_time = time.time()
    while time.time() < start_time + timeout:
        result = _run_cmd(host, cmd, hide=True)
        if result:
            return result.stdout

    return ""


def run_ok(host: str, cmd: str) -> bool:
    """
    Run a command and return true if the execution was ok
    """

    result = _run_cmd(host, cmd, hide=True)
    return result.ok


def run_background(host: str, cmd: str) -> None:
    """
    Run a command in the background
    """

    cmd = f"{config.BASH_TOOL} -l -c \"{cmd}\""
    if host == "":
        invoke.run(cmd, warn=True, disown=True)
    else:
        conn = Connection(host)
        conn.run(cmd, warn=True, disown=True)
