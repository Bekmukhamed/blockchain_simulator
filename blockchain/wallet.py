from dataclasses import dataclass

@dataclass
class Wallet:
    wallet_id: int
    balance: int

    def send_transaction(self, receiver, amount, fee, pool, timestamp, tx_id):
        from blockchain.transaction import Transaction
        tx = Transaction(
            transaction_id=tx_id,
            sender=self.wallet_id,
            receiver=receiver,
            amount=amount,
            timestamp=timestamp,
            fee=fee
        )
        pool.add_transaction(tx)