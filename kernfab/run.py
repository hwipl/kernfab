"""
Module for running commands
"""

import invoke                   # type: ignore
from fabric import Connection   # type: ignore


def run_cmd(host: str, cmd: str) -> str:
    """
    Run a command
    """

    cmd = f"bash -l -c \"{cmd}\""
    if host == "":
        result = invoke.run(cmd, warn=True)
    else:
        conn = Connection(host)
        result = conn.run(cmd, warn=True)
    return result.stdout


def run_background(host: str, cmd: str) -> None:
    """
    Run a command in the background
    """

    cmd = f"bash -l -c \"{cmd}\""
    if host == "":
        invoke.run(cmd, warn=True, disown=True)
    else:
        conn = Connection(host)
        conn.run(cmd, warn=True, disown=True)
