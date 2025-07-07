from dataclasses import dataclass
    
@dataclass
class Node:
    node_id: int
    blocks_id: set
    neighbors: set     