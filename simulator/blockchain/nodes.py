from dataclasses import dataclass
from typing import Set, List
from simulator.blockchain.block import Block

@dataclass
class Node:
    """Network node implementation"""
    node_id: int
    neighbors: Set[int]
    stored_blocks: Set[int] = None
    
    def __post_init__(self):
        if self.stored_blocks is None:
            self.stored_blocks = set()
    
    def receive_block(self, block: Block, all_nodes: List['Node']) -> bool:
        """Receive and validate a new block"""
        if block.header.block_id not in self.stored_blocks:
            self.stored_blocks.add(block.header.block_id)
            return True
        return False
    
    def broadcast_block(self, block: Block, all_nodes: List['Node']):
        """Broadcast block to neighbors"""
        for neighbor_id in self.neighbors:
            if neighbor_id < len(all_nodes):
                neighbor = all_nodes[neighbor_id]
                neighbor.receive_block(block, all_nodes)