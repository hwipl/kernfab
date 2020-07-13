"""
Module for building the kernel
"""

from kernfab import config, run


def build() -> None:
    """
    Build kernel
    """

    build_host = ""
    build_cmd = f"make -j{config.BUILDJOBS} tarxz-pkg"
    output = run.run_cmd(build_host, build_cmd)

    # get name of file from output
    parts = output.split()
    if parts:
        # get file name and extract kernel version from filename
        file_name = parts[-1]
        version = "-".join(file_name.split("-")[1:-1])
        print("Built kernel version:", version)
        print("Saved kernel in file:", file_name)
