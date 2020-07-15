"""
Main part of kernfab
"""

import argparse
from kernfab import build, install, qemu

VERSION = "0.1"


def _build(_args) -> None:
    """
    Build kernel
    """

    print("Build kernel")
    build.build()


def _install(_args) -> None:
    """
    Install kernel
    """

    print("Install kernel")
    install.install()


def _qemu(_args) -> None:
    """
    qemu specific command handling
    """

    qemu.qemu()


def _parse_args() -> None:
    """
    Parse command line arguments.
    """

    # create main parser
    parser = argparse.ArgumentParser(
        description="Run the kernfab linux kernel development tool.")
    parser.add_argument("--version", action="version", version=VERSION)
    parser.set_defaults(func=None)

    # add subcommand parsers
    subparsers = parser.add_subparsers(title="subcommands",
                                       description="valid subcommands",
                                       help="list of subcommands")

    # create the parser for the "build" command
    parser_build = subparsers.add_parser("build", help="build kernel")
    parser_build.set_defaults(func=_build)

    # create the parser for the "install" command
    parser_install = subparsers.add_parser("install", help="install kernel")
    parser_install.set_defaults(func=_install)

    # create the parser for the "qemu" command
    parser_qemu = subparsers.add_parser("qemu", help="qemu commands")
    parser_qemu.set_defaults(func=_qemu)

    # parse arguments and call subcommand functions
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        # no subcommand, show help
        parser.print_help()


# main entry point
def main() -> None:
    """
    Main entry point
    """

    # parse command line arguments
    _parse_args()
