from dataclasses import dataclass

@dataclass
class Wallet:
    wallet_id: int
    balance: float
    transactions_sent: int = 0
    total_fees_paid: float = 0

    def send_transaction(self, receiver, amount, fee, pool, timestamp, tx_id):
        # Validate balance
        # if self.balance < (amount + fee):
        #     raise ValueError(f"Insufficient balance: {self.balance} < {amount + fee}")
            
        from blockchain.transaction import Transaction
        tx = Transaction(
            transaction_id=tx_id,
            sender=self.wallet_id,
            receiver=receiver,
            amount=amount,
            timestamp=timestamp,
            fee=fee
        )
        
        # Deduct from sender balance immediately
        self.balance -= (amount + fee)
        self.transactions_sent += 1
        self.total_fees_paid += fee
        pool.add_transaction(tx)
        
    def receive_payment(self, amount):
        """Called when transaction is confirmed in block"""
        self.balance += amount