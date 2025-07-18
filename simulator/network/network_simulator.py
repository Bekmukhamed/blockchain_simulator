import simpy
import random
import json
from typing import Dict, List

class NetworkSimulator:
    """Enhanced network simulation for extra credit"""
    
    def __init__(self, config):
        self.config = config
        self.load_network_configs()
    
    def load_network_configs(self):
        """Load network configuration from JSON files"""
        try:
            with open('config/network.json', 'r') as f:
                self.network_config = json.load(f)
            
            with open('config/network/latency.json', 'r') as f:
                self.latency_config = json.load(f)
        except FileNotFoundError:
            # Use default network settings
            self.network_config = {
                "latency_profiles": {
                    "global": {"min_ms": 50, "max_ms": 300, "average_ms": 150}
                }
            }
            self.latency_config = {}
    
    def propagate_block(self, block, start_node_id, nodes, metrics):
        """Simulate realistic block propagation"""
        # Calculate delays for all nodes
        total_delay = 0
        for node_id in range(len(nodes)):
            if node_id != start_node_id:
                # Calculate network latency
                latency = self.get_network_latency(start_node_id, node_id)
                
                # Calculate bandwidth delay based on block size
                bandwidth_delay = self.get_bandwidth_delay(block.header.size)
                
                # Total propagation delay in seconds
                delay = (latency + bandwidth_delay) / 1000
                total_delay = max(total_delay, delay)  # Use max delay
                
                # Update metrics
                metrics.io_requests += 1
                metrics.network_data += block.header.size / (1024 * 1024)  # MB
                
        return total_delay
    
    def get_network_latency(self, from_node: int, to_node: int) -> float:
        """Calculate network latency between nodes in milliseconds"""
        profile = self.network_config["latency_profiles"]["global"]
        return random.uniform(profile["min_ms"], profile["max_ms"])
    
    def get_bandwidth_delay(self, block_size_bytes: int) -> float:
        """Calculate bandwidth delay based on block size"""
        bandwidth_mbps = 100  # 100 Mbps average
        bandwidth_bytes_per_ms = (bandwidth_mbps * 1000000) / (8 * 1000)
        return block_size_bytes / bandwidth_bytes_per_ms