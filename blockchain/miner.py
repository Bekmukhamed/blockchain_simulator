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

    def mine_block(self, parent_block_id, pool, block_id, timestamp, blocksize):
        transactions = pool.transactions_limit(blocksize)
        header = Header(
            block_id=block_id,
            parent_block_id=parent_block_id,
            timestamp=timestamp,
            time_since_last_block=0,  # You can compute this if needed
            transaction_count=len(transactions)
        )
        block = Block(header=header, transactions=transactions)
        # print(f"Miner {self.miner_id} mined block {block_id} with {len(transactions)} transactions.")
        return block, [transaction.transaction_id for transaction in transactions]