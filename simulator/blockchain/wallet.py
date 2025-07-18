from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Wallet:
    wallet_id: int
    balance: float
    transactions_sent: int = 0
    total_fees_paid: float = 0

    region: str = ""
    transaction_history: List[str] = None


    def __post_init__(self):
        if self.transaction_history is None:
            self.transaction_history = []


    def send_transaction(self, receiver, amount, fee, pool, timestamp, transaction_id):
        # Validate balance
        # if self.balance < (amount + fee):
        #     raise ValueError(f"Insufficient balance: {self.balance} < {amount + fee}")
        
        if self.balance < (amount + fee):
            raise ValueError(f"Insufficient balance: {self.balance} < {amount + fee}")

        from blockchain.core.transaction import Transaction
        transaction = Transaction(
            transaction_id=transaction_id,
            sender=self.wallet_id,
            receiver=receiver,
            amount=amount,
            timestamp=timestamp,
            fee=fee
        )
        
        self.balance -= (amount + fee)
        self.transactions_sent += 1
        self.total_fees_paid += fee
        self.transaction_history.append(transaction_id)
        pool.add_transaction(transaction)
        

    def receive_payment(self, amount):
        """Called when transaction is confirmed in block"""
        self.balance += amount

    
    def get_effective_balance(self):
        return max(0, self.balance)