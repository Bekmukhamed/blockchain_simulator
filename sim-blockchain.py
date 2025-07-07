#!/usr/bin/env python3

"""
This is the main entry point for the blockchain simulator.
"""

import sys
from blockchain import cli

def main():
    argv = sys.argv[1:]
    args = cli.parse_args(argv)
    config = cli.build_config(args)
    print(config)


if __name__ == "__main__":
    main()