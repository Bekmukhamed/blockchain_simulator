import simpy
from typing import List
from simulator.blockchain.wallet import Wallet
from simulator.blockchain.transaction_pool import Transaction_pool
from simulator.core.metrics import SimulationMetrics

class WalletProcessManager:
    """Manages wallet processes for transaction generation"""
    
    def __init__(self, env: simpy.Environment, config):
        self.env = env
        self.config = config
    
    def create_wallets(self, wallet_count: int) -> List[Wallet]:
        """Create wallet instances with starting balance"""
        wallets = []
        for i in range(wallet_count):
            wallet = Wallet(
                wallet_id=i,
                balance=1000.0  # Starting balance for transactions
            )
            wallets.append(wallet)
        return wallets
    
    def wallet_process(self, wallet: Wallet, transaction_pool: Transaction_pool, metrics: SimulationMetrics):
        """SimPy process for wallet transaction generation"""
        for tx_num in range(self.config.transactions):
            # Generate transaction to next wallet (round-robin)
            receiver = (wallet.wallet_id + 1) % self.config.wallets
            tx_id = f"{wallet.wallet_id}-{tx_num}"
            
            try:
                wallet.send_transaction(
                    receiver=receiver,
                    amount=1.0,
                    fee=0.01,
                    pool=transaction_pool,
                    timestamp=int(self.env.now),
                    transaction_id=tx_id
                )
                metrics.total_transactions += 1
                metrics.pending_transactions += 1
            except ValueError:
                # Insufficient balance - skip transaction
                pass
            
            # Wait for transaction interval
            yield self.env.timeout(self.config.interval)