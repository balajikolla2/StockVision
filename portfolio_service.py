"""
services/portfolio_service.py
Service handling portfolio operations, buying and selling stocks for investors.
"""

from typing import List, Optional, Dict
from storage.file_handler import FileHandler
from models.investor import Investor
from models.portfolio import Portfolio, Holding
from services.stock_service import StockService
from services.transaction_service import TransactionService
from login import AuthService
from utils import (
    InsufficientFundsError, InsufficientStockError, InvalidInputError
)

class PortfolioService:
    PORTFOLIO_HEADERS = ["user_id", "ticker", "quantity", "avg_buy_price"]
    PORTFOLIO_FILE = "portfolio.txt"

    def __init__(self, file_handler: Optional[FileHandler] = None, 
                 stock_service: Optional[StockService] = None,
                 transaction_service: Optional[TransactionService] = None,
                 auth_service: Optional[AuthService] = None):
        self.file_handler = file_handler or FileHandler()
        self.file_handler.ensure_file_exists(self.PORTFOLIO_FILE, self.PORTFOLIO_HEADERS)
        self.stock_service = stock_service or StockService(self.file_handler)
        self.transaction_service = transaction_service or TransactionService(self.file_handler)
        self.auth_service = auth_service or AuthService(self.file_handler)

    def load_portfolio(self, investor: Investor) -> Portfolio:
        """
        Loads an investor's holdings from portfolio.txt into their Portfolio model instance.
        """
        records = self.file_handler.read_records(self.PORTFOLIO_FILE)
        portfolio = Portfolio(user_id=investor.user_id)

        for r in records:
            if r.get("user_id") == investor.user_id:
                ticker = r.get("ticker", "")
                qty = int(r.get("quantity", 0))
                avg_price = float(r.get("avg_buy_price", 0.0))
                if qty > 0:
                    portfolio.holdings[ticker] = Holding(ticker, qty, avg_price)

        investor.portfolio = portfolio
        return portfolio

    def _save_all_portfolios(self, user_id: str, portfolio: Portfolio) -> bool:
        """
        Writes updated portfolio holdings to portfolio.txt.
        """
        all_records = self.file_handler.read_records(self.PORTFOLIO_FILE)
        # Filter out records for this user
        other_records = [r for r in all_records if r.get("user_id") != user_id]

        user_records = [h.to_dict(user_id) for h in portfolio.get_all_holdings()]
        combined = other_records + user_records

        return self.file_handler.write_records(self.PORTFOLIO_FILE, self.PORTFOLIO_HEADERS, combined)

    def buy_stock(self, investor: Investor, ticker: str, quantity: int) -> Dict[str, str]:
        """
        Executes stock purchase:
        1. Checks stock availability in market catalog.
        2. Validates investor wallet balance.
        3. Deducts wallet balance & updates market stock supply.
        4. Updates investor portfolio & saves to storage.
        5. Logs transaction.
        """
        if quantity <= 0:
            raise InvalidInputError("Quantity to buy must be greater than zero.")

        stock = self.stock_service.get_stock(ticker)
        if not stock:
            raise InvalidInputError(f"Stock symbol '{ticker}' does not exist.")

        if stock.available_quantity < quantity:
            raise InsufficientStockError(
                f"Market only has {stock.available_quantity} shares of {stock.ticker} available."
            )

        total_cost = stock.price * quantity
        if investor.wallet.balance < total_cost:
            raise InsufficientFundsError(
                f"Insufficient wallet funds! Total cost: ${total_cost:,.2f}, Available balance: ${investor.wallet.balance:,.2f}"
            )

        # Ensure portfolio is populated
        self.load_portfolio(investor)

        # Deduct wallet funds
        investor.wallet.withdraw(total_cost)
        self.auth_service.update_user_record(investor)

        # Update stock inventory
        self.stock_service.update_stock_quantity(stock.ticker, -quantity)

        # Update portfolio
        investor.portfolio.add_or_update_holding(stock.ticker, quantity, stock.price)
        self._save_all_portfolios(investor.user_id, investor.portfolio)

        # Log transaction
        txn = self.transaction_service.record_transaction(
            user_id=investor.user_id,
            ticker=stock.ticker,
            trade_type="BUY",
            quantity=quantity,
            price=stock.price
        )

        return txn

    def sell_stock(self, investor: Investor, ticker: str, quantity: int) -> Dict[str, str]:
        """
        Executes stock sale:
        1. Validates investor owns sufficient shares.
        2. Calculates sale proceeds.
        3. Adds proceeds to wallet balance & updates market stock supply.
        4. Updates investor portfolio & saves to storage.
        5. Logs transaction.
        """
        if quantity <= 0:
            raise InvalidInputError("Quantity to sell must be greater than zero.")

        self.load_portfolio(investor)
        holding = investor.portfolio.get_holding(ticker)
        if not holding or holding.quantity < quantity:
            owned = holding.quantity if holding else 0
            raise InsufficientStockError(
                f"You only own {owned} shares of {ticker.upper()}. Cannot sell {quantity} shares."
            )

        stock = self.stock_service.get_stock(ticker)
        # If stock not in catalog, fallback to buy price for selling valuation
        current_price = stock.price if stock else holding.avg_buy_price

        sale_proceeds = current_price * quantity

        # Update wallet balance
        investor.wallet.deposit(sale_proceeds)
        self.auth_service.update_user_record(investor)

        # Increase market stock supply if stock exists
        if stock:
            self.stock_service.update_stock_quantity(stock.ticker, quantity)

        # Update portfolio
        investor.portfolio.remove_or_reduce_holding(ticker, quantity)
        self._save_all_portfolios(investor.user_id, investor.portfolio)

        # Log transaction
        txn = self.transaction_service.record_transaction(
            user_id=investor.user_id,
            ticker=ticker.upper(),
            trade_type="SELL",
            quantity=quantity,
            price=current_price
        )

        return txn
