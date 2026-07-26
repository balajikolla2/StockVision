"""
models/wallet.py
Wallet class managing funds for investor users.
"""

from utils import InsufficientFundsError, InvalidInputError

class Wallet:
    def __init__(self, user_id: str, balance: float = 0.0):
        self.user_id = user_id
        self.balance = float(balance)

    def deposit(self, amount: float) -> float:
        """Deposits funds into the wallet."""
        if amount <= 0:
            raise InvalidInputError("Deposit amount must be greater than zero.")
        self.balance += amount
        return self.balance

    def withdraw(self, amount: float) -> float:
        """Deducts funds from the wallet if sufficient balance exists."""
        if amount <= 0:
            raise InvalidInputError("Withdrawal amount must be greater than zero.")
        if amount > self.balance:
            raise InsufficientFundsError(
                f"Insufficient wallet funds! Available balance: ${self.balance:,.2f}, Requested: ${amount:,.2f}"
            )
        self.balance -= amount
        return self.balance

    def __repr__(self) -> str:
        return f"Wallet(user_id={self.user_id}, balance=${self.balance:,.2f})"
