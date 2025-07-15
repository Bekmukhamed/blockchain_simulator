from dataclasses import dataclass

@dataclass
class Config:
    nodes: int = 7
    neighbors: int = 4
    miners: int = 2
    hashrate: int = 1000
    blocktime: int = 10
    difficulty: int = 0 # initialized to T x (K x H) in cli.py
    reward: int = 50
    wallets: int = 5
    transactions: int = 100
    interval: int = 1
    blocksize: int = 1000
    blocks: int = 10
    print: int = 144  # Changed from bool to int with default 144
    debug: bool = False
    halving: int = 210000  # Default Bitcoin halving schedule

    def __post_init__(self):
        if self.nodes < self.miners:
            raise ValueError("Number of miners cannot exceed number of nodes.")
        if self.neighbors >= self.nodes or self.neighbors*self.nodes%2 != 0:
            raise ValueError("Number of neighbors is wrong.")
        if self.neighbors < 0:
            raise ValueError("Number of neighbors cannot be negative.")
        if self.hashrate <= 0:
            raise ValueError("Hashrate must be a positive integer.")
        if self.blocktime <= 0:
            raise ValueError("Block time must be a positive integer.")
        if self.difficulty < 0:
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
        if not isinstance(self.print, int) or self.print <= 0:
            raise ValueError("Print interval must be a positive integer")
        if self.debug not in [True, False]:
            raise ValueError("Debug mode must be a boolean value.")
        
    # def __str__(self):
    #     return (f"Config (nodes={self.nodes}, neighbors={self.neighbors}, miners={self.miners}, hashrate={self.hashrate}, "
    #             f"blocktime={self.blocktime}, difficulty={self.difficulty}, reward={self.reward}, "
    #             f"wallets={self.wallets}, transactions={self.transactions}, interval={self.interval}, "
    #             f"blocksize={self.blocksize}, blocks={self.blocks}, print={self.print}, "
    #             f"debug={self.debug}, halving={self.halving})")
    
    # def init_parameters():

BLOCKCHAIN_CONFIGS = {
    'BTC': {
        'reward': 50,
        'halving': 210000,
        'blocktime': 600,
        'blocksize': 1000000,  # 1 MB
        'max_tx': 4000
    },
    'BCH': {
        'reward': 12.5,
        'halving': 210000,
        'blocktime': 600,
        'blocksize': 32000000,  # 32 MB
        'max_tx': 128000
    },
    'LTC': {
        'reward': 50,
        'halving': 840000,
        'blocktime': 150,
        'blocksize': 1000000,  # 1 MB
        'max_tx': 4000
    },
    'DOGE': {
        'reward': 10000,
        'halving': None,  # No halving
        'blocktime': 60,
        'blocksize': 1000000,  # 1 MB
        'max_tx': 4000
    },
    'MEMO': {
        'reward': 51.8457072,
        'halving': 9644000,
        'blocktime': 3.27,
        'blocksize': 8000000,  # 8 MB
        'max_tx': 32000
    }
}

WORKLOAD_CONFIGS = {
    'SMALL': {
        'wallets': 10,
        'transactions': 10,
        'interval': 10.0
    },
    'MEDIUM': {
        'wallets': 1000,
        'transactions': 1000,
        'interval': 1.0
    },
    'LARGE': {
        'wallets': 1000,
        'transactions': 1000,
        'interval': 0.01
    }
}

