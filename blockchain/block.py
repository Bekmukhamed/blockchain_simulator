from dataclasses import dataclass

# Block structure: Each block has a header (1,024 bytes) + (# transactions × 256
# bytes). Track block ID, timestamp, time-since-last-block, transaction count, and size.
@dataclass
class Header:
    block_id: int
    parent_block_id: int
    timestamp: int
    time_since_last_block: int
    transaction_count: int
    size: int = 1024

    def update_size(self, transactions_count, tx_size_bytes=256):
        """Update size based on header + transaction sizes"""
        self.size = 1024 + (transactions_count * tx_size_bytes)
        self.transaction_count = transactions_count

@dataclass
class Block: 
    header: Header          # should be 1 mb
    transactions: list      # each transaction should be 256 bytes

    def __post_init__(self):
        self.header.update_size(len(self.transactions))