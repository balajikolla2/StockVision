"""
services/transaction_service.py
Service handling recording and querying of trade transactions.
"""

from typing import List, Optional, Dict
from datetime import datetime
import uuid
from storage.file_handler import FileHandler

class TransactionService:
    TRANSACTION_HEADERS = ["transaction_id", "user_id", "ticker", "type", "quantity", "price", "total_amount", "timestamp"]
    TRANSACTIONS_FILE = "transactions.txt"

    def __init__(self, file_handler: Optional[FileHandler] = None):
        self.file_handler = file_handler or FileHandler()
        self.file_handler.ensure_file_exists(self.TRANSACTIONS_FILE, self.TRANSACTION_HEADERS)

    def record_transaction(self, user_id: str, ticker: str, trade_type: str, 
                           quantity: int, price: float) -> Dict[str, str]:
        """
        Logs a trade transaction (BUY or SELL) to transactions.txt.
        """
        total_amount = quantity * price
        t_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        record = {
            "transaction_id": t_id,
            "user_id": user_id,
            "ticker": ticker.upper(),
            "type": trade_type.upper(),
            "quantity": str(quantity),
            "price": f"{price:.2f}",
            "total_amount": f"{total_amount:.2f}",
            "timestamp": timestamp
        }

        self.file_handler.append_record(self.TRANSACTIONS_FILE, self.TRANSACTION_HEADERS, record)
        return record

    def get_all_transactions(self) -> List[Dict[str, str]]:
        """Returns all recorded transactions system-wide."""
        return self.file_handler.read_records(self.TRANSACTIONS_FILE)

    def get_user_transactions(self, user_id: str) -> List[Dict[str, str]]:
        """Returns transaction history for a specific user ID."""
        records = self.get_all_transactions()
        return [r for r in records if r.get("user_id") == user_id]
