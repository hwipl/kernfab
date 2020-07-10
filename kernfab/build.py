"""
Module for building the kernel
"""

from kernfab import run

# number of simultaneous build jobs to run
BUILDJOBS = 32


def build() -> None:
    """
    Build kernel
    """

    build_host = ""
    build_cmd = f"make -j{BUILDJOBS} tarxz-pkg"
    run.run_cmd(build_host, build_cmd)
