import argparse
from pathlib import Path
import sys

from .oot import oot_cli_command


def dragex_command(argv):
    parser = argparse.ArgumentParser(
        prog=f"{Path(sys.argv[0]).name} --command dragex",
    )
    subparsers = parser.add_subparsers()
    oot_cli_command.add_subparser(subparsers)
    args = parser.parse_args(argv)
    # subparsers are expected to set a "func" default for the subparser,
    # to be used as a callback
    res = args.func(args)
    assert res is not None
    return res
