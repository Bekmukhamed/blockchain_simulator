from dataclasses import dataclass
from uuid import uuid4
    
@dataclass
class Transaction:
    transaction_id: int
    sender: str
    receiver: str
    amount: float
    timestamp: int
    fee: int

    @staticmethod
    def create_transaction(sender, receiver, amount, timestamp, fee):
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")
        return Transaction(transaction_id=uuid4().hex, sender=sender, receiver=receiver, amount=amount, timestamp=timestamp, fee=fee)