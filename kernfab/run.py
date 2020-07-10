"""
Module for running commands
"""

import invoke                   # type: ignore
from fabric import Connection   # type: ignore


def run_cmd(host: str, cmd: str) -> None:
    """
    Run a command
    """

    cmd = f"bash -l -c \"{cmd}\""
    if host == "":
        invoke.run(cmd, warn=True)
    else:
        conn = Connection(host)
        conn.run(cmd, warn=True)
