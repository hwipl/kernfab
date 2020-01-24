"""
Main part of kernfab
"""

import argparse

VERSION = "0.1"


def parse_args() -> None:
    """
    Parse command line arguments.
    """

    # if we add more, consider moving it to config or somewhere else
    parser = argparse.ArgumentParser(
        description="Run the kernfab linux kernel development tool.")
    parser.add_argument("--version", action="version", version=VERSION)
    parser.parse_args()


# main entry point
def main() -> None:
    """
    Main entry point
    """

    # parse command line arguments
    parse_args()
