#!/usr/bin/env python3

"""
This is the main entry point for the blockchain simulator.
"""

import sys
import time
from random import random
from blockchain import cli
from blockchain.nodes import Node
from blockchain.block import Block, Header
from blockchain.miner import Miner
from blockchain.transaction import Transaction
from blockchain.wallet import Wallet
from blockchain.network import stub_pairing
from dataclasses import dataclass

class Simulation: 
    def __init__(self, config):
        self.config = config
        self.nodes = []
        self.wallets = []
        # This is the global unconfirmed transaction pool (mempool)
        self.transaction_pool = []
        # self.blockchain = []  # A simple list representing the canonical chain
        self.start_time = 0
        self.io_requests = 0 # global variable incremented when a node stores a new block and broadcasts it to neighbors. NOTE: ignore duplicates
        self.network_data = 0 # stores all broadcasted block sizes. NOTE: ignore duplicates 

    def setup(self):
        print("--- Setting up the simulation ---")

        # Create nodes
        for id in range(self.config.nodes):
            node = Node(node_id=id, blocks_id=set(), neighbors=set())
            self.nodes.append(node)
        print(f"Created {len(self.nodes)} nodes.")


def main():
    # FIXME: move time measurement to a starting point (or somewhere else)
    start_time = time.perf_counter()
    # parse the arguments
    argv = sys.argv[1:]
    args = cli.parse_args(argv)
    config = cli.get_config_from_cli()
    print(config)


    # create N peer nodes 
    nodes_list = []
    
    # print(f"Created {len(nodes_list)} nodes. Nodes : {nodes_list} \n")


    # randomly connect each node to --neighbors M distinct peers
    if config.nodes * config.neighbors % 2 != 0:
        print("Error: The product of nodes and neighbors must be even.")
        sys.exit(1)
        

    # create transactions
    transactions = []
    for id in range(3):
        transaction = Transaction(transaction_id=id, sender=f"sender {id}", receiver=f"receiver {id}", amount=random(), timestamp=0, fee=0)
        transactions.append(transaction)
    # print(f"Transactions: {transactions} \n")

    # create blocks
    for id in range(config.blocks):
        header = Header(block_id=id, parent_block_id=id-1 if id > 0 else 0, timestamp=0, time_since_last_block=0, transaction_count=len(transactions))
        block = Block(header=header, transactions=transactions)
        # print(f"Block {id} created: {block} \n")
    
    

    # miner
    miner = Miner(miner_id=0, hashrate=config.hashrate, blocktime=config.blocktime, difficulty=config.difficulty, reward=config.reward)
    # print(f"Miner created: {miner} \n")
    
    # connect nodes
    stub_pairing(nodes_list, config.neighbors)
    print(f"Neighbors after pairing: {[node.neighbors for node in nodes_list]} \n")

    # initialize difficulty (??? in config)

    # issue R coins per block 

    # generate W wallets 
    wallet_list = []
    for id in range(config.wallets):
        wallet = Wallet()
        wallet_list.append(wallet)

    # each wallet will send X transactions into the global unconfirmed pool at interval I seconds
    
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    #print(f"[{elapsed_time:.2f}] Sum B:{blocks}/{totalBlocks} {complete}% abt:{avg_block_time} tps:{confirmed_tx_per_sec} infl:{inflation}% ETA:{seconds}s Diff:{xx}M H:{xx}M Tx:{total_tx} C:{coins}K Pool:{pending_tx} NMB:{network_MB} IO:{io_requests}")

    #print(f"[******] End B:blocks abt:avg_block_time(s) tps:confirmed_tx_per_sec Tx:total_tx C:coins NMB:network_MB IO:io_requests")

if __name__ == "__main__":
    main()