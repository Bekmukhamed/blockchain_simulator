#!/usr/bin/env python3

"""
This is the main entry point for the blockchain simulator.
"""

import sys
from random import random
from blockchain import cli
from blockchain.nodes import Node
# from blockchain import config

def main():
    # parse the arguments
    argv = sys.argv[1:]
    args = cli.parse_args(argv)
    config = cli.get_config_from_cli()
    print(config)

    # create N peer nodes 
    for id in range(config.nodes):
        Node.node_id = id
        # print(Node.node_id)

    # randomly connect each node to --neighbors M distinct peers
    for id in range(config.nodes):
        for _ in range():
            ...

    # for _ in range(config.miners):
        

    # initialize difficulty (??? in config)

    # issue R coins per block 

    # generate W wallets 

if __name__ == "__main__":
    main()