from dataclasses import dataclass
    
@dataclass
class Node:
    blocks_id: set
    neighbors: set     