#!/usr/bin/env python3

"""
This is the main entry point for the blockchain simulator.
"""

import sys
import time
import simpy
from random import random, expovariate
from blockchain import cli
from blockchain.nodes import Node
from blockchain.block import Block, Header
from blockchain.miner import Miner
from blockchain.transaction import Transaction
from blockchain.wallet import Wallet
from blockchain.network import stub_pairing
from blockchain.transaction_pool import Transaction_pool
from dataclasses import dataclass

class Simulation: 
    def __init__(self, config):
        self.env = simpy.Environment()
        self.config = config
        self.nodes = []
        self.miners = []
        self.wallets = []
        self.transaction_pool = Transaction_pool()
        self.blocks = []
        
        self.io_requests = 0 # global variable incremented when a node stores a new block and broadcasts it to neighbors. NOTE: ignore duplicates
        self.network_data = 0 # stores all broadcasted block sizes. NOTE: ignore duplicates 

        self.coin_supply = 0
        self.last_block_time = None
        self.block_times = []
        self.total_transactions = 0

    def setup(self):
        print("--- Setting up the simulation ---")
        # Wallets → TransactionPool → Miner selects → Block → Node broadcasts → Neighbors receive → Pool pruning
        
        # Create nodes
        for id in range(self.config.nodes):
            node = Node(node_id=id, blocks_id=set(), neighbors=set())
            self.nodes.append(node)
        print(f"Created {len(self.nodes)} nodes.")
        
        # Connect nodes
        stub_pairing(self.nodes, self.config.neighbors)
        print(f"Neighbors after pairing: {[node.neighbors for node in self.nodes]} \n")

        # Generate wallets
        for id in range(self.config.wallets):
            wallet = Wallet(wallet_id=id, balance=random())
            self.wallets.append(wallet)

        # Spawn miners
        for id in range(self.config.miners):
            self.miners.append(Miner(miner_id=id, hashrate=self.config.hashrate, blocktime=self.config.blocktime, difficulty=self.config.difficulty, reward=self.config.reward))



    # func responsible for wallets generating transactions
    # def wallet_send_transaction(self):
    #     transaction_id = 0
    #     for wallet in self.wallets:
    #         for _ in range(self.config.transactions):
    #             receiver = (wallet.wallet_id + 1) % self.config.wallets
    #             wallet.send_transaction(
    #                 receiver=receiver,
    #                 amount=1.0,
    #                 fee=0,
    #                 pool=self.transaction_pool,
    #                 timestamp=int(time.time()),
    #                 tx_id=f"{wallet.wallet_id}-{transaction_id}"
    #             )
    #             transaction_id += 1
    #             yield self.env.timeout(self.config.interval)
    #     print(f"Transaction pool after wallets: {[transaction.transaction_id for transaction in self.transaction_pool.transactions]}")

    def wallet_process(self, wallet):
        for tx_num in range(self.config.transactions):
            receiver = (wallet.wallet_id + 1) % self.config.wallets
            wallet.send_transaction(
                receiver=receiver,
                amount=1.0,
                fee=0,
                pool=self.transaction_pool,
                timestamp=int(self.env.now),
                tx_id=f"{wallet.wallet_id}-{tx_num}"
            )
            self.total_transactions += 1
            yield self.env.timeout(self.config.interval)
            
    def miner_process(self, miner):
        block_id = 1
        parent_block_id = 0
        while len(self.blocks) < self.config.blocks:
            total_hashrate = self.config.miners * self.config.hashrate
            mining_time = expovariate(total_hashrate / self.config.difficulty)
            yield self.env.timeout(mining_time)
            block, included_tx_ids = miner.mine_block(
                parent_block_id=parent_block_id,
                pool=self.transaction_pool,
                block_id=block_id,
                timestamp=int(self.env.now),
                blocksize=self.config.blocksize
            )
            self.blocks.append(block)
            self.coin_supply += miner.reward
            self.last_block_time = self.env.now
            self.block_times.append(block.header.time_since_last_block)
            parent_block_id = block_id
            block_id += 1
            self.env.process(self.propagate_block(block, 0))
            self.transaction_pool.remove_confirmed_transaction(set(included_tx_ids))
            if self.config.print and len(self.blocks) % self.config.print == 0:
                self.print_summary()
            if len(self.blocks) >= self.config.blocks:
                break


    # def miner_mine_blocks(self):
    #     while True:
    #         yield self.env.timeout(1)  # Simulate mining time
    #         miner = self.miners[0]
    #         parent_block_id = 0 if not self.blocks else self.blocks[-1].header.block_id
    #         block_id = 1 if not self.blocks else self.blocks[-1].header.block_id + 1
    #         timestamp = int(time.time())
    #         block, included_transaction_ids = miner.mine_block(
    #             parent_block_id=parent_block_id,
    #             pool=self.transaction_pool,
    #             block_id=block_id,
    #             timestamp=timestamp,
    #             blocksize=self.config.blocksize
    #         )
    #         self.blocks.append(block)
    #         self.env.process(self.node_broadcasts_block(block))
    #         self.prune_pool(included_transaction_ids)
    #         if len(self.blocks) >= self.config.blocks:
    #             break


    # def node_broadcasts_block(self, block):
    #     yield self.env.timeout(0)  # No delay, but must be a generator
    #     print("Node 0 broadcasting block...")
    #     self.nodes[0].receive_block(block, self.nodes)

    # def prune_pool(self, included_tx_ids):
    #     self.transaction_pool.remove_confirmed_transaction(set(included_tx_ids))
    #     print(f"Transaction pool after mining: {[tx.transaction_id for tx in self.transaction_pool.transactions]}")


    # def run(self):
    #     self.setup()
    #     # Additional simulation logic can be added here
    #     self.env.process(self.wallet_send_transaction())

    #     # Create blocks 
    #     self.env.process(self.create_blocks())

    #     # block, included_transaction_ids = self.env.process(self.miner_mine_blocks())
    #     # self.env.process(self.node_broadcasts_block(block))
    #     # self.env.prune_pool(included_transaction_ids)

    #     self.env.run(until=100)
    #     print("Simulation run complete.")


    def propagate_block(self, block, start_node_id):
        queue = [start_node_id]
        seen = set()
        while queue:
            node_id = queue.pop(0)
            if node_id in seen:
                continue
            seen.add(node_id)
            node = self.nodes[node_id]
            if block.header.block_id not in node.blocks_id:
                node.blocks_id.add(block.header.block_id)
                self.io_requests += 1
                self.network_data += 1024 + 256 * block.header.transaction_count
                for neighbor_id in node.neighbors:
                    queue.append(neighbor_id)
            yield self.env.timeout(0)

    def print_summary(self):
        blocks = len(self.blocks)
        total_blocks = self.config.blocks
        complete = 100 * blocks / total_blocks
        abt = sum(self.block_times) / len(self.block_times) if self.block_times else 0
        tps = (blocks * self.config.blocksize) / self.env.now if self.env.now else 0
        coins = self.coin_supply
        print(f"[{self.env.now:.2f}] Sum B:{blocks}/{total_blocks} {complete:.1f}% abt:{abt:.2f}s tps:{tps:.2f} C:{coins} Pool:{len(self.transaction_pool.transactions)} NMB:{self.network_data/1e6:.2f} IO:{self.io_requests}")

    def run(self):
        self.setup()
        for wallet in self.wallets:
            self.env.process(self.wallet_process(wallet))
        for miner in self.miners:
            self.env.process(self.miner_process(miner))
        self.env.run(until=None)
        self.print_summary()
        print("Simulation run complete.")

# def main():
#     argv = sys.argv[1:]
#     args = cli.parse_args(argv)
#     config = cli.get_config_from_cli()
#     print(config)

#     start_time = time.perf_counter()

#     sim = Simulation(config)
#     sim.run()

#     end_time = time.perf_counter()
#     elapsed_time = end_time - start_time

    #print(f"[{elapsed_time:.2f}] Sum B:{blocks}/{totalBlocks} {complete}% abt:{avg_block_time} tps:{confirmed_tx_per_sec} infl:{inflation}% ETA:{seconds}s Diff:{xx}M H:{xx}M Tx:{total_tx} C:{coins}K Pool:{pending_tx} NMB:{network_MB} IO:{io_requests}")
    #print(f"[******] End B:blocks abt:avg_block_time(s) tps:confirmed_tx_per_sec Tx:total_tx C:coins NMB:network_MB IO:io_requests")

def main():
    config = cli.get_config_from_cli()
    print(config)
    sim = Simulation(config)
    sim.run()
if __name__ == "__main__":
    main()