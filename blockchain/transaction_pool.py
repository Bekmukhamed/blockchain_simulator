from dataclasses import dataclass, field
from blockchain.transaction import Transaction

@dataclass
class Transaction_pool:
    transactions: list = field(default_factory=list)

    def add_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)
   
    def transactions_limit(self, limit):
        transactions = self.transactions[:limit]
        self.transactions = self.transactions[limit:]
        return transactions
    
    def remove_confirmed_transaction(self, transaction_ids):
        self.transactions = [transaction for transaction in self.transactions if transaction.transaction_id not in transaction_ids]
    