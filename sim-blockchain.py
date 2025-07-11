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

        # Calculate blocks per year based on block time
        # blocks_per_day = int(86400 / self.config.blocktime)  # 86400 seconds in a day
        blocks_per_day = 50
        self.config.blocks = blocks_per_day  # 1 year simulation

    def setup(self):
        # print("--- Setting up the simulation ---")
        # Wallets → TransactionPool → Miner selects → Block → Node broadcasts → Neighbors receive → Pool pruning
        
        # Create nodes
        for id in range(self.config.nodes):
            node = Node(node_id=id, blocks_id=set(), neighbors=set())
            self.nodes.append(node)
        # print(f"Created {len(self.nodes)} nodes.")
        # Connect nodes
        stub_pairing(self.nodes, self.config.neighbors)
        # print(f"Neighbors after pairing: {[node.neighbors for node in self.nodes]} \n")

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
        last_block_time = self.env.now
        blocks_since_retarget = 0
        blocks_since_halving = 0
        current_reward = miner.reward
        
        while len(self.blocks) < self.config.blocks:
            total_hashrate = self.config.miners * self.config.hashrate
            mining_time = expovariate(total_hashrate / self.config.difficulty)
            yield self.env.timeout(mining_time)
            
            if len(self.blocks) >= self.config.blocks:
                break
                
            current_time = self.env.now
            time_since_last = current_time - last_block_time
            
            block, included_tx_ids = miner.mine_block(
                parent_block_id=parent_block_id,
                pool=self.transaction_pool,
                block_id=block_id,
                timestamp=int(current_time),
                blocksize=self.config.blocksize
            )
            
            block.header.time_since_last_block = time_since_last
            
            self.blocks.append(block)
            self.coin_supply += miner.reward
            self.block_times.append(time_since_last)
            last_block_time = current_time
            
            parent_block_id = block_id
            block_id += 1
            
            self.env.process(self.propagate_block(block, 0))
            self.transaction_pool.remove_confirmed_transaction(set(included_tx_ids))
            
            blocks_since_retarget += 1
            blocks_since_halving += 1

            # Difficulty retargeting every 2016 blocks
            if blocks_since_retarget >= 2016:
                actual_time = sum(self.block_times[-2016:])
                target_time = self.config.blocktime * 2016
                self.config.difficulty = int(self.config.difficulty * (target_time / actual_time))
                blocks_since_retarget = 0

            # Reward halving
            if hasattr(self.config, 'halving') and self.config.halving:
                if blocks_since_halving >= self.config.halving:
                    current_reward = max(current_reward // 2, 0)
                    blocks_since_halving = 0
            
            # Print progress based on interval or debug mode
            if self.config.debug or (len(self.blocks) % self.config.print == 0):
                self.print_summary()


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
        complete = min(100 * blocks / total_blocks, 100.0)  # Cap at 100%
        
        # Calculate average block time
        if len(self.block_times) > 1:
            abt = sum(self.block_times[1:]) / (len(self.block_times) - 1)  # Skip first block
        else:
            abt = 0
        
        # Calculate transactions per second
        tps = self.total_transactions / self.env.now if self.env.now > 0 else 0
        
        # Calculate ETA
        remaining_blocks = max(total_blocks - blocks, 0)
        eta = remaining_blocks * abt if abt > 0 else 0
        
        # Calculate inflation rate
        prev_supply = self.coin_supply - self.miners[0].reward if blocks > 1 else self.miners[0].reward
        inflation = ((self.coin_supply - prev_supply) / prev_supply * 100) if prev_supply > 0 else 0
        
        # Format values with appropriate units
        diff_str = f"{self.config.difficulty/1e6:.1f}M"
        hash_str = f"{self.config.hashrate/1e3:.1f}K"  # Changed to K since hashrate is 1000
        coins_str = f"{self.coin_supply/1e3:.1f}K"
        nmb_str = f"{self.network_data/1e6:.2f}"
        
        # Use consistent format with sample output
        print(
            f"[{self.env.now:.2f}] "
            f"Sum B:{blocks}/{total_blocks} "
            f"{complete:.1f}% "
            f"abt:{abt:.2f}s "
            f"tps:{tps:.2f} "
            f"infl:{inflation:.2f}% "
            f"ETA:{eta:.2f}s "
            f"Diff:{diff_str} "
            f"H:{hash_str} "
            f"Tx:{self.total_transactions} "
            f"C:{coins_str} "
            f"Pool:{len(self.transaction_pool.transactions)} "
            f"NMB:{nmb_str} "
            f"IO:{self.io_requests}"
        )

    def run(self):
        self.setup()
        for wallet in self.wallets:
            self.env.process(self.wallet_process(wallet))
        for miner in self.miners:
            self.env.process(self.miner_process(miner))
        self.env.run(until=None)
        self.print_summary()
        # print("Simulation run complete.")

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
    # print(config)
    sim = Simulation(config)
    sim.run()
if __name__ == "__main__":
    main()