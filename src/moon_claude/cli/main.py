"""CLI 入口"""


import argparse
import sys

from moon_claude.cli.commands.version import cmd_version


def main() -> None:
    parser = argparse.ArgumentParser(prog="moon", description="MoonClaude CLI")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("ping", help="Ping the core daemon")

    args = parser.parse_args()

    if args.version:
        cmd_version()
        return

    else:
        parser.print_help()
        sys.exit(1)
