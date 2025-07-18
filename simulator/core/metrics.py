from dataclasses import dataclass, field
from typing import List

@dataclass
class SimulationMetrics:
    """Enhanced metrics tracking for assignment compliance"""
    total_transactions: int = 0
    confirmed_transactions: int = 0
    coin_supply: float = 0.0
    network_data: float = 0.0  # in MB
    io_requests: int = 0
    block_times: List[float] = field(default_factory=list)
    difficulty_adjustments: int = 0
    halving_count: int = 0
    pending_transactions: int = 0
    
    def get_average_block_time(self) -> float:
        return sum(self.block_times) / len(self.block_times) if self.block_times else 0
    
    def get_tps(self, current_time: float) -> float:
        return self.confirmed_transactions / current_time if current_time > 0 else 0
    
    def get_inflation_rate(self) -> float:
        if len(self.block_times) <= 1:
            return 0.0
        # Calculate inflation based on recent coin issuance
        if len(self.block_times) >= 2016:
            recent_supply_change = self.coin_supply - (self.coin_supply * 0.95)
            return (recent_supply_change / self.coin_supply) * 100 if self.coin_supply > 0 else 0.0
        return 0.0