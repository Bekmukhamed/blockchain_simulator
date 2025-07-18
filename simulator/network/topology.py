import random
from typing import List
from simulator.blockchain.nodes import Node

class Network_topology:
    """Network topology management"""
    
    def __init__(self):
        pass
    
    def create_network(self, nodes: List[Node], node_count: int, neighbors: int):
        """Create network topology"""
        # Create nodes
        for i in range(node_count):
            node = Node(node_id=i, neighbors=set())
            nodes.append(node)
        
        # Create connections using stub pairing
        self._stub_pairing(nodes, neighbors)
    
    def _stub_pairing(self, nodes: List[Node], neighbors: int):
        """Implement stub pairing algorithm"""
        stubs = []
        
        # Create stubs for each node
        for node in nodes:
            for _ in range(neighbors):
                stubs.append(node.node_id)
        
        # Randomly pair stubs
        random.shuffle(stubs)
        
        # Connect pairs
        for i in range(0, len(stubs), 2):
            if i + 1 < len(stubs):
                node1_id = stubs[i]
                node2_id = stubs[i + 1]
                
                if node1_id != node2_id:  # Avoid self-connections
                    nodes[node1_id].neighbors.add(node2_id)
                    nodes[node2_id].neighbors.add(node1_id)