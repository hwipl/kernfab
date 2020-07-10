"""
Module for building the kernel
"""

import invoke
from fabric import Connection

# number of simultaneous build jobs to run
BUILDJOBS = 32


def do_build(host: str, cmd: str) -> None:
    """
    Run cmd
    """

    # run build command
    cmd = f"bash -l -c \"{cmd}\""
    if host == "":
        invoke.run(cmd, warn=True)
    else:
        conn = Connection(host)
        conn.run(cmd, warn=True)


def build() -> None:
    """
    Build kernel
    """

    build_host = ""
    build_cmd = f"make -j{BUILDJOBS} tarxz-pkg"
    do_build(build_host, build_cmd)
