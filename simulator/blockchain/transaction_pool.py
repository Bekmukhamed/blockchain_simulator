from dataclasses import dataclass, field
from typing import List, Set
from blockchain.core.transaction import Transaction

@dataclass
class Transaction_pool:
    transactions: List[Transaction] = field(default_factory=list)


    def add_transaction(self, transaction: Transaction):
         if not any(tx.transaction_id == transaction.transaction_id for tx in self.transactions):
            self.transactions.append(transaction)
   

    def get_transactions_by_priority(self, limit: int) -> List[Transaction]:
        # Get transactions ordered by priority (fee per byte)
        # Sort by priority (highest first) then by timestamp (oldest first)
        sorted_transactions = sorted(
            self.transactions, 
            key=lambda tx: (-tx.priority, tx.timestamp)
        )
        
        selected = sorted_transactions[:limit]
        # Remove selected transactions from pool
        self.transactions = [tx for tx in self.transactions if tx not in selected]
        return selected


    def transactions_limit(self, limit):
        return self.get_transactions_by_priority(limit)
    

    def remove_confirmed_transaction(self, transaction_ids):
        self.transactions = [transaction for transaction in self.transactions if transaction.transaction_id not in transaction_ids]
    

    def get_pool_size(self):
        return len(self.transactions)
        
    def get_total_fees(self):
        return sum(tx.fee for tx in self.transactions)