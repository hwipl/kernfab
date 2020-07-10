"""
Module for installing the kernel
"""

import invoke
from fabric import Connection


def do_install(host: str, cmd: str) -> None:
    """
    Run install cmd
    """

    # run build command
    cmd = f"bash -l -c \"{cmd}\""
    if host == "":
        invoke.run(cmd, warn=True)
    else:
        conn = Connection(host)
        conn.run(cmd, warn=True)


def install() -> None:
    """
    Install kernel
    """

    install_host = ""
    install_cmd = ""
    do_install(install_host, install_cmd)
