from dataclasses import dataclass

@dataclass
class Miner:
    miner_id: int
    hashrate: int
    blocktime: int
    difficulty: int
    reward: int

    def mine_block(self, block):
        print(f"Miner {self.miner_id} is mining block {block.block_id} with hashrate {self.hashrate}.")
        return True