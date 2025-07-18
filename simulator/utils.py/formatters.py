def format_number(num: float, suffix: str = "") -> str:
    """Format numbers with appropriate suffixes"""
    if num >= 1e6:
        return f"{num/1e6:.1f}M{suffix}"
    elif num >= 1e3:
        return f"{num/1e3:.1f}K{suffix}"
    else:
        return f"{num:.1f}{suffix}"

def format_simulation_output(metrics, current_time: float, config) -> str:
    """Format simulation output to match assignment requirements"""
    blocks_completed = len(metrics.blocks) if hasattr(metrics, 'blocks') else 0
    completion_pct = (blocks_completed / config.blocks) * 100
    
    avg_block_time = metrics.get_average_block_time()
    tps = metrics.get_tps(current_time)
    inflation = metrics.get_inflation_rate()
    
    eta = (config.blocks - blocks_completed) * avg_block_time if avg_block_time > 0 else 0
    
    return (f"[{current_time:.2f}] Sum B:{blocks_completed}/{config.blocks} "
            f"{completion_pct:.1f}% abt:{avg_block_time:.2f}s tps:{tps:.2f} "
            f"infl:{inflation:.2f}% ETA:{eta:.2f}s "
            f"Diff:{format_number(config.difficulty)} "
            f"H:{format_number(config.miners * config.hashrate)} "
            f"Tx:{metrics.total_transactions} C:{format_number(metrics.coin_supply)} "
            f"Pool:{metrics.pending_transactions} "
            f"NMB:{metrics.network_data:.2f} IO:{metrics.io_requests}")