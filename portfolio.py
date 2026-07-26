"""
models/portfolio.py
Portfolio and Holding models representing an investor's stock holdings.
"""

from typing import Dict, List

class Holding:
    def __init__(self, ticker: str, quantity: int, avg_buy_price: float):
        self.ticker = ticker.upper()
        self.quantity = int(quantity)
        self.avg_buy_price = float(avg_buy_price)

    @property
    def total_invested(self) -> float:
        return self.quantity * self.avg_buy_price

    def to_dict(self, user_id: str) -> Dict[str, str]:
        return {
            "user_id": user_id,
            "ticker": self.ticker,
            "quantity": str(self.quantity),
            "avg_buy_price": f"{self.avg_buy_price:.2f}"
        }

    def __repr__(self) -> str:
        return f"Holding({self.ticker}: qty={self.quantity}, avg_price=${self.avg_buy_price:.2f})"


class Portfolio:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.holdings: Dict[str, Holding] = {}  # ticker -> Holding object

    def add_or_update_holding(self, ticker: str, quantity: int, price: float) -> Holding:
        """
        Adds new shares or updates weighted average buy price when purchasing stock.
        """
        ticker = ticker.upper()
        if ticker in self.holdings:
            existing = self.holdings[ticker]
            new_qty = existing.quantity + quantity
            new_total_cost = (existing.quantity * existing.avg_buy_price) + (quantity * price)
            new_avg_price = new_total_cost / new_qty
            existing.quantity = new_qty
            existing.avg_buy_price = new_avg_price
            return existing
        else:
            holding = Holding(ticker, quantity, price)
            self.holdings[ticker] = holding
            return holding

    def remove_or_reduce_holding(self, ticker: str, quantity: int) -> int:
        """
        Reduces shares when selling stock. Returns remaining shares in holding.
        """
        ticker = ticker.upper()
        if ticker not in self.holdings:
            raise KeyError(f"No holdings found for ticker {ticker}")
        
        holding = self.holdings[ticker]
        if quantity > holding.quantity:
            raise ValueError(f"Cannot sell {quantity} shares; only {holding.quantity} owned.")

        holding.quantity -= quantity
        remaining_qty = holding.quantity
        if holding.quantity == 0:
            del self.holdings[ticker]
        
        return remaining_qty

    def get_holding(self, ticker: str) -> Holding:
        """Returns holding for given ticker or None."""
        return self.holdings.get(ticker.upper())

    def get_all_holdings(self) -> List[Holding]:
        """Returns list of all active holdings."""
        return list(self.holdings.values())

    def __repr__(self) -> str:
        return f"Portfolio(user_id={self.user_id}, total_positions={len(self.holdings)})"
