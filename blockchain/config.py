from dataclasses import dataclass
    

@dataclass
class Config:
    nodes: int = 10
    neighbors: int = 3
    miners: int = 2
    hashrate: int = 1000
    blocktime: int = 10
    difficulty: int = 1
    reward: int = 50
    wallets: int = 5
    transactions: int = 100
    interval: int = 1
    blocksize: int = 1000
    blocks: int = 10
    print: bool = False
    debug: bool = False

    def __post_init__(self):
        if self.nodes < self.miners:
            raise ValueError("Number of miners cannot exceed number of nodes.")
        if self.neighbors < 0:
            raise ValueError("Number of neighbors cannot be negative.")
        if self.hashrate <= 0:
            raise ValueError("Hashrate must be a positive integer.")
        if self.blocktime <= 0:
            raise ValueError("Block time must be a positive integer.")
        if self.difficulty <= 0:
            raise ValueError("Difficulty must be a positive integer.")
        if self.reward <= 0:
            raise ValueError("Reward must be a positive integer.")
        if self.wallets <= 0:
            raise ValueError("Number of wallets must be a positive integer.")
        if self.transactions < 0:
            raise ValueError("Number of transactions cannot be negative.")
        if self.interval <= 0:
            raise ValueError("Interval must be a positive integer.")
        if self.blocksize <= 0:
            raise ValueError("Block size must be a positive integer.")
        if self.blocks <= 0:
            raise ValueError("Number of blocks must be a positive integer.")
        if self.print not in [True, False]:
            raise ValueError("Print blocks must be a boolean value.")
        if self.debug not in [True, False]:
            raise ValueError("Debug mode must be a boolean value.")
        
    def __str__(self):
        return (f"Config (nodes={self.nodes}, neighbors={self.neighbors}, miners={self.miners}, hashrate={self.hashrate}, "
                f"blocktime={self.blocktime}, difficulty={self.difficulty}, reward={self.reward}, "
                f"wallets={self.wallets}, transactions={self.transactions}, interval={self.interval}, "
                f"blocksize={self.blocksize}, blocks={self.blocks}, print={self.print}, "
                f"debug={self.debug})")