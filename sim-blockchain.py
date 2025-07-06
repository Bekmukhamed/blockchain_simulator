#!/usr/bin/env python3

"""
This is the main entry point for the blockchain simulator.
"""

import sys
from blockchain.cli import parse_args, build_config

def main():
    argv = sys.argv[1:]
    args = parse_args(argv)
    config = build_config(args)
    print(config)


if __name__ == "__main__":
    main()