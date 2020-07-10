"""
Module for installing the kernel
"""

from kernfab import run


def install() -> None:
    """
    Install kernel
    """

    install_host = ""
    install_cmd = ""
    run.run_cmd(install_host, install_cmd)
