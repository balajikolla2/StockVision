"""
models/investor.py
Investor class inheriting from User. Represents retail/institutional investor users with wallet & portfolio management.
"""

from models.user import User
from models.wallet import Wallet
from models.portfolio import Portfolio
from typing import Dict

class Investor(User):
    def __init__(self, user_id: str, username: str, password_hash: str, email: str, 
                 wallet_balance: float = 0.0, risk_preference: str = "Medium"):
        super().__init__(user_id, username, password_hash, email, role="investor")
        self.wallet = Wallet(user_id=user_id, balance=wallet_balance)
        self.portfolio = Portfolio(user_id=user_id)
        self.risk_preference = risk_preference.capitalize()

    def get_dashboard_type(self) -> str:
        return "Investor Portal & Trading Dashboard"

    def to_dict(self) -> Dict[str, str]:
        data = super().to_dict()
        data["balance"] = f"{self.wallet.balance:.2f}"
        data["risk_preference"] = self.risk_preference
        return data

    def __repr__(self) -> str:
        return f"Investor(id={self.user_id}, username='{self.username}', balance=${self.wallet.balance:,.2f})"
