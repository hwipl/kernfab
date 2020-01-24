"""
Main part of kernfab
"""

import argparse

VERSION = "0.1"


def build(_args) -> None:
    """
    Build kernel
    """

    print("Build kernel")


def parse_args() -> None:
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
    parser_build.set_defaults(func=build)

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
    parse_args()
