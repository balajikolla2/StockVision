"""
services/report_service.py
Service generating analytical and performance reports for Investors and Administrators.
"""

from typing import Dict, List, Optional
from models.investor import Investor
from services.stock_service import StockService
from services.portfolio_service import PortfolioService
from services.transaction_service import TransactionService
from storage.file_handler import FileHandler
from utils import format_currency, format_percentage

class ReportService:
    def __init__(self, file_handler: Optional[FileHandler] = None,
                 stock_service: Optional[StockService] = None,
                 portfolio_service: Optional[PortfolioService] = None,
                 transaction_service: Optional[TransactionService] = None):
        self.file_handler = file_handler or FileHandler()
        self.stock_service = stock_service or StockService(self.file_handler)
        self.portfolio_service = portfolio_service or PortfolioService(self.file_handler, self.stock_service)
        self.transaction_service = transaction_service or TransactionService(self.file_handler)

    def generate_investor_report(self, investor: Investor) -> Dict:
        """
        Generates comprehensive financial and performance analytics for an Investor.
        """
        portfolio = self.portfolio_service.load_portfolio(investor)
        holdings = portfolio.get_all_holdings()

        total_invested = 0.0
        total_market_val = 0.0
        holding_details = []

        for h in holdings:
            stock = self.stock_service.get_stock(h.ticker)
            current_price = stock.price if stock else h.avg_buy_price
            
            cost_basis = h.quantity * h.avg_buy_price
            market_val = h.quantity * current_price
            pnl = market_val - cost_basis
            roi_pct = (pnl / cost_basis * 100) if cost_basis > 0 else 0.0

            total_invested += cost_basis
            total_market_val += market_val

            holding_details.append({
                "ticker": h.ticker,
                "quantity": h.quantity,
                "avg_buy_price": h.avg_buy_price,
                "current_price": current_price,
                "cost_basis": cost_basis,
                "market_value": market_val,
                "pnl": pnl,
                "roi_pct": roi_pct
            })

        total_pnl = total_market_val - total_invested
        overall_roi = (total_pnl / total_invested * 100) if total_invested > 0 else 0.0
        total_net_worth = investor.wallet.balance + total_market_val

        # Get transaction counts
        user_txns = self.transaction_service.get_user_transactions(investor.user_id)
        buy_count = sum(1 for t in user_txns if t.get("type") == "BUY")
        sell_count = sum(1 for t in user_txns if t.get("type") == "SELL")

        return {
            "investor_name": investor.username,
            "email": investor.email,
            "risk_preference": investor.risk_preference,
            "cash_balance": investor.wallet.balance,
            "total_invested": total_invested,
            "total_market_value": total_market_val,
            "net_worth": total_net_worth,
            "total_pnl": total_pnl,
            "overall_roi": overall_roi,
            "holdings": holding_details,
            "total_trades": len(user_txns),
            "buy_trades": buy_count,
            "sell_trades": sell_count
        }

    def generate_admin_report(self) -> Dict:
        """
        Generates system-wide market summary and trading volume analytics for Admins.
        """
        users = self.file_handler.read_records("users.txt")
        investor_count = sum(1 for u in users if u.get("role") == "investor")
        admin_count = sum(1 for u in users if u.get("role") == "admin")

        stocks = self.stock_service.get_all_stocks()
        total_stocks = len(stocks)
        total_inventory = sum(s.available_quantity for s in stocks)
        market_cap = sum(s.price * s.available_quantity for s in stocks)

        txns = self.transaction_service.get_all_transactions()
        total_txns = len(txns)
        trading_volume = sum(float(t.get("total_amount", 0.0)) for t in txns)

        return {
            "total_users": len(users),
            "investor_count": investor_count,
            "admin_count": admin_count,
            "total_stocks_listed": total_stocks,
            "total_shares_available": total_inventory,
            "market_cap": market_cap,
            "total_transactions": total_txns,
            "total_trading_volume": trading_volume
        }
