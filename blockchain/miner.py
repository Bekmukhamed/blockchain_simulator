from dataclasses import dataclass
from blockchain.block import Block, Header
from blockchain.transaction_pool import Transaction_pool

@dataclass
class Miner:
    miner_id: int
    hashrate: int
    blocktime: int
    difficulty: int
    reward: int

    def mine_block(self, parent_block_id, pool, block_id, timestamp, blocksize, wallets_dict):
        transactions = pool.transactions_limit(blocksize)
        
        # Calculate total fees
        total_fees = sum(tx.fee for tx in transactions)
        total_reward = self.reward + total_fees
        
        # Process transactions - update wallet balances
        for tx in transactions:
            sender_wallet = wallets_dict[tx.sender]
            receiver_wallet = wallets_dict[tx.receiver]
            receiver_wallet.receive_payment(tx.amount)
        
        # Miner gets block reward + fees
        miner_wallet = wallets_dict.get(f"miner_{self.miner_id}")
        if miner_wallet:
            miner_wallet.receive_payment(total_reward)
        
        header = Header(
            block_id=block_id,
            parent_block_id=parent_block_id,
            timestamp=timestamp,
            time_since_last_block=0,
            transaction_count=len(transactions)
        )
        block = Block(header=header, transactions=transactions)
        return block, [transaction.transaction_id for transaction in transactions]