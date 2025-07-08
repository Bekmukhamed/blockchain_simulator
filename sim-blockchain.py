#!/usr/bin/env python3

"""
This is the main entry point for the blockchain simulator.
"""

import sys
from random import random
from blockchain import cli
from blockchain.nodes import Node
from blockchain.block import Block, Header
from blockchain.miner import Miner
from blockchain.transaction import Transaction
from blockchain.wallet import Wallet
from blockchain.network import stub_pairing

def main():
    # parse the arguments
    argv = sys.argv[1:]
    args = cli.parse_args(argv)
    config = cli.get_config_from_cli()
    print(config)


    # create N peer nodes 
    nodes_list = []
    for id in range(config.nodes):
        node = Node(node_id=id, blocks_id=set(), neighbors=set())
        nodes_list.append(node)
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


if __name__ == "__main__":
    main()