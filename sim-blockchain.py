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
        
        self.io_requests = 0
        self.network_data = 0
        self.coin_supply = 0
        self.last_block_time = None
        self.block_times = []
        self.total_transactions = 0
        self.halving_count = 0


    def setup(self):
        # Create nodes
        for id in range(self.config.nodes):
            node = Node(node_id=id, blocks_id=set(), neighbors=set())
            self.nodes.append(node)
        
        # Connect nodes
        stub_pairing(self.nodes, self.config.neighbors)
        
        # Generate wallets
        for id in range(self.config.wallets):
            wallet = Wallet(wallet_id=id, balance=random())
            self.wallets.append(wallet)

        # Spawn miners
        for id in range(self.config.miners):
            self.miners.append(Miner(
                miner_id=id, 
                hashrate=self.config.hashrate, 
                blocktime=self.config.blocktime, 
                difficulty=self.config.difficulty, 
                reward=self.config.reward
            ))

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
        
        # Create wallets dictionary for miner
        wallets_dict = {wallet.wallet_id: wallet for wallet in self.wallets}
        # Add miner wallets
        wallets_dict[f"miner_{miner.miner_id}"] = Wallet(
            wallet_id=f"miner_{miner.miner_id}", 
            balance=0.0
        )
        
        while len(self.blocks) < self.config.blocks:
            total_hashrate = self.config.miners * self.config.hashrate
            difficulty = max(self.config.difficulty, 1)
            mining_time = expovariate(total_hashrate / difficulty)
            yield self.env.timeout(mining_time)
                
            current_time = self.env.now
            time_since_last = current_time - last_block_time
            
            block, included_tx_ids = miner.mine_block(
                parent_block_id=parent_block_id,
                pool=self.transaction_pool,
                block_id=block_id,
                timestamp=int(current_time),
                blocksize=self.config.blocksize,
                wallets_dict=wallets_dict  # Add this parameter
            )
            # Only count the mining reward transaction here
            # (wallet transactions already counted in wallet_process)
            self.total_transactions += 1  # Mining reward only
            block.header.time_since_last_block = time_since_last
            
            self.blocks.append(block)
            self.coin_supply += current_reward
            self.block_times.append(time_since_last)
            last_block_time = current_time
            
            # Check if we've reached the target - if so, break immediately
            if len(self.blocks) >= self.config.blocks:
                yield from self.propagate_block(block, 0)
                self.transaction_pool.remove_confirmed_transaction(set(included_tx_ids))
                if self.config.debug or (len(self.blocks) % self.config.print == 0):
                    self.print_summary()
                break
            
            blocks_since_retarget += 1
            blocks_since_halving += 1

            if blocks_since_retarget >= 2016:
                if len(self.block_times) >= 2016:
                    actual_time = sum(self.block_times[-2016:])
                    target_time = self.config.blocktime * 2016
                    new_diff = int(difficulty * (target_time / actual_time))
                    self.config.difficulty = max(new_diff, 1)
                    blocks_since_retarget = 0

            if (self.config.halving and 
                blocks_since_halving >= self.config.halving and 
                self.halving_count < 35):
                current_reward = current_reward / 2
                for m in self.miners:
                    m.reward = current_reward
                blocks_since_halving = 0
                self.halving_count += 1
                if self.halving_count >= 35:
                    current_reward = 0
                    
            yield from self.propagate_block(block, 0)
            self.transaction_pool.remove_confirmed_transaction(set(included_tx_ids))
            
            parent_block_id = block_id
            block_id += 1

            # Check termination conditions
            if hasattr(self.config, 'years') or self.config.blocks > 10:
                # For long simulations (years specified or many blocks), 
                # only check block count, not transaction completion
                if len(self.blocks) >= self.config.blocks:
                    break
            else:
                # For short simulations, use original termination logic
                all_wallets_done = all(
                    wallet.transactions_sent >= self.config.transactions 
                    for wallet in self.wallets
                )
                all_transactions_confirmed = len(self.transaction_pool.transactions) == 0
                
                if all_wallets_done and all_transactions_confirmed:
                    print("All transactions processed, stopping simulation")
                    break
                    
            if self.config.debug or (len(self.blocks) % self.config.print == 0):
                self.print_summary()

    def propagate_block(self, block, start_node_id):
        queue = [(start_node_id, 0)]  # (node_id, delay)
        seen = {start_node_id}
        
        while queue:
            node_id, accumulated_delay = queue.pop(0)
            node = self.nodes[node_id]
            
            if block.header.block_id not in node.blocks_id:
                node.blocks_id.add(block.header.block_id)
                self.io_requests += 1
                self.network_data += block.header.size
                
                # Realistic network delay calculation
                bandwidth_delay = block.header.size / (self.get_bandwidth_profile() * 1024 * 1024 / 8)  # Convert Mbps to bytes/sec
                network_latency = self.get_network_latency(start_node_id, node_id)
                total_delay = accumulated_delay + bandwidth_delay + network_latency
                
                # Ensure propagation happens within blocktime
                if total_delay < self.config.blocktime:
                    yield self.env.timeout(total_delay)
                    
                    # Add neighbors with accumulated delay
                    for neighbor_id in node.neighbors:
                        if neighbor_id not in seen:
                            seen.add(neighbor_id)
                            queue.append((neighbor_id, total_delay))

    def get_network_latency(self, from_node, to_node):
        """Use config/network/latency.json geographic latency matrix"""
        import json
        import random
        
        # Load latency config
        with open('config/network/latency.json', 'r') as f:
            latency_config = json.load(f)
        
        # For simplicity, assign nodes to regions based on node_id
        regions = list(latency_config['locations'].keys())
        from_region = regions[from_node % len(regions)]
        to_region = regions[to_node % len(regions)]
        
        if from_region in latency_config['locations'] and to_region in latency_config['locations'][from_region]:
            latency_data = latency_config['locations'][from_region][to_region]
            # Use normal distribution with provided parameters
            import numpy as np
            if latency_data['distribution'] == 'norm':
                mean, std = eval(latency_data['parameters'])
                latency_ms = max(np.random.normal(mean, std), latency_data['min_ms'])
                return min(latency_ms / 1000.0, latency_data['max_ms'] / 1000.0)  # Convert to seconds
        
        # Fallback to simple latency
        return random.uniform(0.001, 0.1)

    def get_bandwidth_profile(self):
        """Use config/network.json bandwidth profiles"""
        import json
        import random
        
        # Load network config
        with open('config/network.json', 'r') as f:
            network_config = json.load(f)
        
        # Select random bandwidth profile
        profiles = list(network_config['bandwidth_profiles'].values())
        return random.choice(profiles)  # Return Mbps

    def print_summary(self):
        blocks = len(self.blocks)
        total_blocks = self.config.blocks
        complete = min(100 * blocks / total_blocks, 100.0)
        
        # Calculate average block time
        if len(self.block_times) > 1:
            abt = sum(self.block_times[1:]) / (len(self.block_times) - 1)
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
        
        # Format values
        diff_str = f"{self.config.difficulty/1e6:.1f}M"
        hash_str = f"{self.config.hashrate * self.config.miners/1e6:.1f}M"  # Total hashrate
        coins_str = f"{self.coin_supply/1e3:.1f}K"
        nmb_str = f"{self.network_data/1e6:.2f}"
        
        # Fix pool count - should show pending transactions
        pool_count = len(self.transaction_pool.transactions)
        
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
            f"Pool:{pool_count} "
            f"NMB:{nmb_str} "
            f"IO:{self.io_requests}"
        )

    def run(self):
        self.setup()
        
        # Start wallet processes
        for wallet in self.wallets:
            self.env.process(self.wallet_process(wallet))
        
        # Start miner processes
        for miner in self.miners:
            self.env.process(self.miner_process(miner))
        
        # Add trace event processing if trace file exists
        import os
        if os.path.exists('traces/bitcoin_2024.json'):
            self.env.process(self.trace_event_process())
        
        # Run simulation
        try:
            self.env.run()
        except Exception as e:
            print(f"Simulation ended: {e}")

        avg_block_time = sum(self.block_times)/len(self.block_times) if self.block_times else 0
        final_tps = self.total_transactions/self.env.now if self.env.now > 0 else 0
        
        print(f"\n[******] End "
              f"B:{len(self.blocks)} "
              f"abt:{avg_block_time:.2f}s "
              f"tps:{final_tps:.2f} "
              f"Tx:{self.total_transactions} "
              f"C:{self.coin_supply/1e3:.1f}K "
              f"NMB:{self.network_data/1e6:.2f} "
              f"IO:{self.io_requests}")

def main():
    config = cli.get_config_from_cli()
    sim = Simulation(config)
    sim.run()

if __name__ == "__main__":
    main()