def validate_config(config) -> None:
    """Validate configuration parameters"""
    if config.nodes < config.miners:
        raise ValueError("Number of miners cannot exceed number of nodes")
    
    if config.neighbors >= config.nodes:
        raise ValueError("Number of neighbors must be less than total nodes")
    
    if config.hashrate <= 0:
        raise ValueError("Hashrate must be positive")
    
    if config.blocktime <= 0:
        raise ValueError("Block time must be positive")

def validate_network_topology(nodes: int, neighbors: int) -> bool:
    """Validate network topology parameters"""
    if neighbors >= nodes:
        return False
    return True