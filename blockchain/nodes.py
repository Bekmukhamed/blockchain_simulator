from dataclasses import dataclass
    
@dataclass
class Node:
    node_id: int
    blocks_id: set
    neighbors: set

    def add_neighbor(self, neighbor_id):
        self.neighbors.add(neighbor_id)
        print(f"Node {self.node_id} added neighbor {neighbor_id}.")

    def receive_block(node, block):
        node.blocks_id.add(block.block_id)
        print(f"Node {node.node_id} received block {block.block_id}.")