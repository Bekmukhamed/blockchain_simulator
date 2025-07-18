from dataclasses import dataclass
from uuid import uuid4
    
@dataclass
class Transaction:
    transaction_id: str
    sender: str
    receiver: str
    amount: float
    timestamp: int
    fee: float
    
    priority: float =0.0


    def __post_init__(self):
        tx_size = 256
        self.priority = self.fee / tx_size


    @staticmethod
    def create_transaction(sender, receiver, amount, timestamp, fee):
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")
        return Transaction(transaction_id=uuid4().hex, sender=sender, receiver=receiver, amount=amount, timestamp=timestamp, fee=fee)