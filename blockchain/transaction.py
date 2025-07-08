from dataclasses import dataclass
    
@dataclass
class Transaction:
    transaction_id: int
    sender: str
    receiver: str
    amount: float
    timestamp: int
    fee: int

    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError("Amount must be greater than zero")
        
    
