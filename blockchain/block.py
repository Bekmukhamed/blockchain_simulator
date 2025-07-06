import dataclasses

# Block structure: Each block has a header (1,024 bytes) + (# transactions × 256
# bytes). Track block ID, timestamp, time-since-last-block, transaction count, and size.
@dataclasses
class Header:
    block_id: int
    timestamp: int
    time_since_last_block: int
    transaction_count: int


@dataclasses
class Block: 
    header: Header          # should be 1 mb
    transactions: list      # each transaction should be 256 bytes