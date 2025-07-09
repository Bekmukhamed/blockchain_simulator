from dataclasses import dataclass
    
@dataclass
class Node:
    node_id: int
    blocks_id: set
    neighbors: set

    # def add_neighbor(self, neighbor_id):
    #     self.neighbors.add(neighbor_id)

    def receive_block(self, block, nodes_list):
        if block.header.block_id in self.blocks_id:
            return
        self.blocks_id.add(block.header.block_id)
        print(f"Node {self.node_id} received block {block.header.block_id}")
        for neighbor_id in self.neighbors:
            nodes_list[neighbor_id].receive_block(block, nodes_list)
        