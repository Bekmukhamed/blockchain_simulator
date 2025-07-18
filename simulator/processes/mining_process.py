import simpy
import random
from typing import List
from simulator.blockchain.miner import Miner
from simulator.blockchain.wallet import Wallet
from simulator.core.metrics import SimulationMetrics

class MiningProcessManager:
    """Manages mining processes for block creation"""
    
    def __init__(self, env: simpy.Environment, config):
        self.env = env
        self.config = config
    
    def create_miners(self, miner_count: int, config) -> List[Miner]:
        """Create miner instances"""
        miners = []
        for i in range(miner_count):
            miner = Miner(
                miner_id=i,
                hashrate=config.hashrate,
                blocktime=config.blocktime,
                difficulty=config.difficulty,
                reward=config.reward
            )
            miners.append(miner)
        return miners
    
    def mining_process(self, miner, wallets, transaction_pool, blocks, metrics, network_simulator):
        """SimPy process for mining blocks with proper exponential distribution"""
        block_id = 1
        parent_block_id = 0
        last_block_time = self.env.now
        blocks_since_retarget = 0
        blocks_since_halving = 0
        current_reward = miner.reward
        current_difficulty = self.config.difficulty
        
        # Create wallets dictionary including miner wallet
        wallets_dict = {wallet.wallet_id: wallet for wallet in wallets}
        wallets_dict[f"miner_{miner.miner_id}"] = Wallet(
            wallet_id=f"miner_{miner.miner_id}",
            balance=0.0
        )
        
        while len(blocks) < self.config.blocks:
            # Calculate mining time using exponential distribution
            # Expected time per block ∼ Exp(total_hashrate / difficulty)
            total_hashrate = self.config.miners * self.config.hashrate
            rate = total_hashrate / current_difficulty
            mining_time = random.expovariate(rate)
            
            # Wait for mining time
            yield self.env.timeout(mining_time)
            
            current_time = self.env.now
            time_since_last = current_time - last_block_time
            
            # Mine block
            block, included_tx_ids = miner.mine_block(
                parent_block_id=parent_block_id,
                pool=transaction_pool,
                block_id=block_id,
                timestamp=int(current_time),
                blocksize=self.config.blocksize,
                wallets_dict=wallets_dict
            )
            
            # Update block timing
            block.header.time_since_last_block = time_since_last
            blocks.append(block)
            metrics.block_times.append(time_since_last)
            metrics.coin_supply += current_reward
            metrics.confirmed_transactions += len(included_tx_ids)
            metrics.pending_transactions -= len(included_tx_ids)
            
            # Block propagation through network
            if hasattr(network_simulator, 'propagate_block'):
                delay = network_simulator.propagate_block(block, miner.miner_id, [], metrics)
                if delay > 0:
                    yield self.env.timeout(delay)
            
            # Remove confirmed transactions from pool
            transaction_pool.remove_confirmed_transaction(set(included_tx_ids))
            
            # Difficulty adjustment every 2016 blocks
            blocks_since_retarget += 1
            if blocks_since_retarget >= 2016:
                current_difficulty = self._adjust_difficulty(
                    current_difficulty, metrics.block_times[-2016:], self.config.blocktime
                )
                blocks_since_retarget = 0
                metrics.difficulty_adjustments += 1
            
            # Halving logic
            blocks_since_halving += 1
            if (self.config.halving and 
                blocks_since_halving >= self.config.halving and 
                metrics.halving_count < 35):
                current_reward = current_reward / 2
                miner.reward = current_reward
                blocks_since_halving = 0
                metrics.halving_count += 1
                if metrics.halving_count >= 35:
                    current_reward = 0
            
            # Print progress
            if self.config.debug or (len(blocks) % self.config.print == 0):
                self._print_summary(blocks, metrics, current_difficulty)
            
            last_block_time = current_time
            parent_block_id = block_id
            block_id += 1
    
    def _adjust_difficulty(self, old_difficulty: int, recent_block_times: List[float], target_blocktime: int) -> int:
        """Adjust difficulty based on actual vs target block time"""
        if len(recent_block_times) < 2016:
            return old_difficulty
        
        actual_time = sum(recent_block_times)
        target_time = target_blocktime * 2016
        
        new_difficulty = int(old_difficulty * (target_time / actual_time))
        return max(1, new_difficulty)
    
    def _print_summary(self, blocks, metrics, difficulty):
        """Print simulation summary in required format"""
        current_time = self.env.now
        blocks_completed = len(blocks)
        completion_pct = (blocks_completed / self.config.blocks) * 100
        
        avg_block_time = metrics.get_average_block_time()
        tps = metrics.get_tps(current_time)
        inflation = metrics.get_inflation_rate()
        eta = (self.config.blocks - blocks_completed) * avg_block_time if avg_block_time > 0 else 0
        
        print(f"[{current_time:.2f}] Sum B:{blocks_completed}/{self.config.blocks} "
              f"{completion_pct:.1f}% abt:{avg_block_time:.2f}s tps:{tps:.2f} "
              f"infl:{inflation:.2f}% ETA:{eta:.2f}s "
              f"Diff:{difficulty/1000000:.1f}M "
              f"H:{self.config.miners * self.config.hashrate/1000000:.0f}M "
              f"Tx:{metrics.total_transactions} C:{metrics.coin_supply:.0f} "
              f"Pool:{metrics.pending_transactions} "
              f"NMB:{metrics.network_data:.2f} IO:{metrics.io_requests}")