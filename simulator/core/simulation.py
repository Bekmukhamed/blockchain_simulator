import simpy
import time
import random
from typing import List
from dataclasses import dataclass, field

from simulator.blockchain.nodes import Node
from simulator.blockchain.miner import Miner
from simulator.blockchain.wallet import Wallet
from simulator.blockchain.block import Block
from simulator.blockchain.transaction_pool import Transaction_pool
from simulator.network.topology import Network_topology

@dataclass
class SimulationMetrics:
    total_transactions: int = 0
    confirmed_transactions: int = 0
    coin_supply: float = 0
    network_data: float = 0  # in MB
    io_requests: int = 0
    block_times: List[float] = field(default_factory=list)
    difficulty_adjustments: int = 0
    halving_count: int = 0
    pending_transactions: int = 0
    
    def get_average_block_time(self):
        return sum(self.block_times) / len(self.block_times) if self.block_times else 0
    
    def get_tps(self, current_time):
        return self.confirmed_transactions / current_time if current_time > 0 else 0
    
    def get_inflation_rate(self):
        if len(self.block_times) <= 1:
            return 0.0
        # Calculate inflation based on recent coin issuance
        if len(self.block_times) >= 2016:
            recent_supply_change = self.coin_supply - (self.coin_supply * 0.95)  # Simplified
            return (recent_supply_change / self.coin_supply) * 100 if self.coin_supply > 0 else 0.0
        return 0.0

class BlockchainSimulation:
    def __init__(self, config):
        self.config = config
        self.env = simpy.Environment()
        
        # Core components
        self.nodes: List[Node] = []
        self.miners: List[Miner] = []
        self.wallets: List[Wallet] = []
        self.transaction_pool = Transaction_pool()
        self.blocks: List[Block] = []
        
        # Simulation state
        self.metrics = SimulationMetrics()
        self.current_difficulty = config.difficulty if config.difficulty > 0 else config.blocktime * (config.miners * config.hashrate)
        self.current_reward = config.reward
        self.last_block_time = 0
        
        # Network topology
        self.topology = Network_topology()
        
    def run(self):
        # Initialize components
        self._setup_network()
        self._setup_miners()
        self._setup_wallets()
        
        # Start processes
        self._start_mining_processes()
        self._start_wallet_processes()
        
        # Run simulation
        self.env.run()
        
        # Print final results
        self._print_final_summary()
    
    def _setup_network(self):
        self.topology.create_network(self.nodes, self.config.nodes, self.config.neighbors)
        
    def _setup_miners(self):
        for i in range(self.config.miners):
            miner = Miner(
                miner_id=i, 
                hashrate=self.config.hashrate, 
                blocktime=self.config.blocktime, 
                difficulty=self.current_difficulty, 
                reward=self.current_reward
            )
            self.miners.append(miner)
            
    def _setup_wallets(self):
        for i in range(self.config.wallets):
            wallet = Wallet(wallet_id=i, balance=1000.0)  # Increased starting balance
            self.wallets.append(wallet)
    
    def _start_mining_processes(self):
        for miner in self.miners:
            self.env.process(self._mining_process(miner))
    
    def _start_wallet_processes(self):
        for wallet in self.wallets:
            self.env.process(self._wallet_process(wallet))
    
    def _mining_process(self, miner):
        block_id = len(self.blocks) + 1
        blocks_since_retarget = 0
        
        while len(self.blocks) < self.config.blocks:
            # Calculate mining time using exponential distribution
            # Expected time per block ∼ Exp(total_hashrate / difficulty)
            total_hashrate = self.config.miners * self.config.hashrate
            rate = total_hashrate / self.current_difficulty
            mining_time = random.expovariate(rate)
            
            # Wait for mining time
            yield self.env.timeout(mining_time)
            
            # Mine the block
            current_time = self.env.now
            time_since_last = current_time - self.last_block_time
            
            # Create wallets dictionary for miner
            wallets_dict = {wallet.wallet_id: wallet for wallet in self.wallets}
            wallets_dict[f"miner_{miner.miner_id}"] = Wallet(
                wallet_id=f"miner_{miner.miner_id}",
                balance=0.0
            )
            
            # Mine block
            block, included_tx_ids = miner.mine_block(
                parent_block_id=block_id - 1,
                pool=self.transaction_pool,
                block_id=block_id,
                timestamp=int(current_time),
                blocksize=self.config.blocksize,
                wallets_dict=wallets_dict
            )
            
            # Update block timing
            block.header.time_since_last_block = time_since_last
            self.blocks.append(block)
            self.metrics.block_times.append(time_since_last)
            self.metrics.coin_supply += self.current_reward
            self.metrics.confirmed_transactions += len(included_tx_ids)
            self.metrics.pending_transactions -= len(included_tx_ids)
            
            # Block propagation
            yield from self._propagate_block(block, miner.miner_id)
            
            # Remove confirmed transactions from pool
            self.transaction_pool.remove_confirmed_transaction(set(included_tx_ids))
            
            # Difficulty adjustment every 2016 blocks
            blocks_since_retarget += 1
            if blocks_since_retarget >= 2016:
                self._adjust_difficulty()
                blocks_since_retarget = 0
            
            # Halving logic
            if (self.config.halving and 
                len(self.blocks) % self.config.halving == 0 and
                self.metrics.halving_count < 35):
                self.current_reward /= 2
                self.metrics.halving_count += 1
                if self.metrics.halving_count >= 35:
                    self.current_reward = 0
            
            # Print progress
            if self.config.debug or len(self.blocks) % self.config.print == 0:
                self._print_progress()
            
            self.last_block_time = current_time
            block_id += 1
    
    def _wallet_process(self, wallet):
        for tx_num in range(self.config.transactions):
            # Generate transaction
            receiver = (wallet.wallet_id + 1) % self.config.wallets
            tx_id = f"{wallet.wallet_id}-{tx_num}"
            
            try:
                wallet.send_transaction(
                    receiver=receiver,
                    amount=1.0,
                    fee=0.01,
                    pool=self.transaction_pool,
                    timestamp=int(self.env.now),
                    transaction_id=tx_id
                )
                self.metrics.total_transactions += 1
                self.metrics.pending_transactions += 1
            except ValueError:
                # Insufficient balance
                pass
            
            # Wait for interval
            yield self.env.timeout(self.config.interval)
    
    def _propagate_block(self, block, miner_id):
        # Simulate block propagation with network delays
        if len(self.nodes) > 0:
            start_node = miner_id % len(self.nodes)
            
            # Propagate to all nodes
            for node in self.nodes:
                if node.node_id != start_node:
                    # Simulate network delay based on block size
                    base_delay = random.uniform(0.1, 1.0)  # 100ms to 1s
                    size_delay = block.header.size / (10 * 1024 * 1024)  # 10 MB/s bandwidth
                    total_delay = base_delay + size_delay
                    
                    yield self.env.timeout(total_delay)
                    
                    # Node receives block
                    if node.receive_block(block, self.nodes):
                        self.metrics.io_requests += 1
                        self.metrics.network_data += block.header.size / (1024 * 1024)  # Convert to MB
    
    def _adjust_difficulty(self):
        if len(self.metrics.block_times) >= 2016:
            recent_times = self.metrics.block_times[-2016:]
            actual_time = sum(recent_times)
            target_time = self.config.blocktime * 2016
            
            self.current_difficulty = int(
                self.current_difficulty * (target_time / actual_time)
            )
            self.current_difficulty = max(1, self.current_difficulty)
            self.metrics.difficulty_adjustments += 1
    
    def _print_progress(self):
        current_time = self.env.now
        blocks_completed = len(self.blocks)
        completion_pct = (blocks_completed / self.config.blocks) * 100
        
        avg_block_time = self.metrics.get_average_block_time()
        tps = self.metrics.get_tps(current_time)
        inflation = self.metrics.get_inflation_rate()
        
        # Calculate ETA
        remaining_blocks = self.config.blocks - blocks_completed
        eta = remaining_blocks * avg_block_time if avg_block_time > 0 else 0
        
        print(f"[{current_time:.2f}] Sum B:{blocks_completed}/{self.config.blocks} "
              f"{completion_pct:.1f}% abt:{avg_block_time:.2f}s tps:{tps:.2f} "
              f"infl:{inflation:.2f}% ETA:{eta:.2f}s "
              f"Diff:{self.current_difficulty/1000000:.1f}M "
              f"H:{self.config.miners * self.config.hashrate/1000000:.0f}M "
              f"Tx:{self.metrics.total_transactions} C:{self.metrics.coin_supply:.0f} "
              f"Pool:{self.metrics.pending_transactions} "
              f"NMB:{self.metrics.network_data:.2f} IO:{self.metrics.io_requests}")
    
    def _print_final_summary(self):
        current_time = self.env.now
        avg_block_time = self.metrics.get_average_block_time()
        tps = self.metrics.get_tps(current_time)
        
        print(f"[******] End B:{len(self.blocks)}/{self.config.blocks} 100.0% "
              f"abt:{avg_block_time:.2f}s tps:{tps:.2f} infl:0.00% "
              f"Diff:{self.current_difficulty/1000000:.1f}M "
              f"H:{self.config.miners * self.config.hashrate/1000000:.0f}M "
              f"Tx:{self.metrics.total_transactions} C:{self.metrics.coin_supply:.0f} "
              f"Pool:{self.metrics.pending_transactions} "
              f"NMB:{self.metrics.network_data:.2f} IO:{self.metrics.io_requests}")