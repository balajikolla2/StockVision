"""
main.py
Application Entry Point for StockVision AI.
Bootstraps services, seeds initial market data if empty, and launches role-based CLI interface.
"""

import os
from storage.file_handler import FileHandler
from login import AuthService
from services.stock_service import StockService
from services.portfolio_service import PortfolioService
from services.transaction_service import TransactionService
from services.recommendation import RecommendationService
from services.report_service import ReportService
from menu import CLIMenu
from utils import hash_password

def seed_initial_data(file_handler: FileHandler) -> None:
    """Seeds default Admin user, sample Investors, and initial Stock market listings if empty."""
    
    # 1. Seed Users
    users_file = "users.txt"
    users = file_handler.read_records(users_file)
    if not users:
        admin_pwd_hash = hash_password("admin123")
        investor1_pwd_hash = hash_password("investor123")
        investor2_pwd_hash = hash_password("investor123")

        initial_users = [
            {
                "user_id": "USR-ADMIN01",
                "username": "admin",
                "password_hash": admin_pwd_hash,
                "email": "admin@stockvision.ai",
                "role": "admin",
                "balance": "0.00",
                "risk_preference": "Medium"
            },
            {
                "user_id": "USR-INV001",
                "username": "john_investor",
                "password_hash": investor1_pwd_hash,
                "email": "john@example.com",
                "role": "investor",
                "balance": "10000.00",
                "risk_preference": "Medium"
            },
            {
                "user_id": "USR-INV002",
                "username": "sarah_trader",
                "password_hash": investor2_pwd_hash,
                "email": "sarah@example.com",
                "role": "investor",
                "balance": "25000.00",
                "risk_preference": "High"
            }
        ]
        file_handler.write_records(users_file, AuthService.USER_HEADERS, initial_users)

    # 2. Seed Stocks
    stocks_file = "stocks.txt"
    stocks = file_handler.read_records(stocks_file)
    if not stocks:
        initial_stocks = [
            {
                "ticker": "AAPL",
                "company_name": "Apple Inc.",
                "price": "195.50",
                "sector": "Tech",
                "available_quantity": "5000",
                "risk_level": "Medium",
                "gainer_pct": "2.45"
            },
            {
                "ticker": "MSFT",
                "company_name": "Microsoft Corp.",
                "price": "420.10",
                "sector": "Tech",
                "available_quantity": "3000",
                "risk_level": "Low",
                "gainer_pct": "1.80"
            },
            {
                "ticker": "NVDA",
                "company_name": "NVIDIA Corporation",
                "price": "125.75",
                "sector": "Tech",
                "available_quantity": "8000",
                "risk_level": "High",
                "gainer_pct": "5.60"
            },
            {
                "ticker": "AMZN",
                "company_name": "Amazon.com Inc.",
                "price": "185.30",
                "sector": "Consumer Cyclical",
                "available_quantity": "4000",
                "risk_level": "Medium",
                "gainer_pct": "-0.75"
            },
            {
                "ticker": "GOOGL",
                "company_name": "Alphabet Inc.",
                "price": "175.20",
                "sector": "Tech",
                "available_quantity": "4500",
                "risk_level": "Medium",
                "gainer_pct": "1.15"
            },
            {
                "ticker": "JPM",
                "company_name": "JPMorgan Chase & Co.",
                "price": "205.80",
                "sector": "Finance",
                "available_quantity": "3500",
                "risk_level": "Low",
                "gainer_pct": "0.40"
            },
            {
                "ticker": "TSLA",
                "company_name": "Tesla Inc.",
                "price": "240.50",
                "sector": "Automotive",
                "available_quantity": "6000",
                "risk_level": "High",
                "gainer_pct": "4.20"
            }
        ]
        file_handler.write_records(stocks_file, StockService.STOCK_HEADERS, initial_stocks)

    # 3. Seed Portfolio Holdings
    portfolio_file = "portfolio.txt"
    portfolios = file_handler.read_records(portfolio_file)
    if not portfolios:
        initial_portfolio = [
            {
                "user_id": "USR-INV001",
                "ticker": "AAPL",
                "quantity": "10",
                "avg_buy_price": "188.00"
            },
            {
                "user_id": "USR-INV001",
                "ticker": "NVDA",
                "quantity": "15",
                "avg_buy_price": "115.00"
            },
            {
                "user_id": "USR-INV002",
                "ticker": "MSFT",
                "quantity": "20",
                "avg_buy_price": "410.00"
            }
        ]
        file_handler.write_records(portfolio_file, PortfolioService.PORTFOLIO_HEADERS, initial_portfolio)

    # 4. Seed Transactions Log
    txns_file = "transactions.txt"
    txns = file_handler.read_records(txns_file)
    if not txns:
        initial_txns = [
            {
                "transaction_id": "TXN-SEED001",
                "user_id": "USR-INV001",
                "ticker": "AAPL",
                "type": "BUY",
                "quantity": "10",
                "price": "188.00",
                "total_amount": "1880.00",
                "timestamp": "2026-07-25 10:30:00"
            },
            {
                "transaction_id": "TXN-SEED002",
                "user_id": "USR-INV001",
                "ticker": "NVDA",
                "type": "BUY",
                "quantity": "15",
                "price": "115.00",
                "total_amount": "1725.00",
                "timestamp": "2026-07-25 11:15:00"
            }
        ]
        file_handler.write_records(txns_file, TransactionService.TRANSACTION_HEADERS, initial_txns)


def main():
    """App bootstrap."""
    file_handler = FileHandler()
    seed_initial_data(file_handler)

    auth_service = AuthService(file_handler)
    stock_service = StockService(file_handler)
    transaction_service = TransactionService(file_handler)
    portfolio_service = PortfolioService(file_handler, stock_service, transaction_service, auth_service)
    recommendation_service = RecommendationService(stock_service)
    report_service = ReportService(file_handler, stock_service, portfolio_service, transaction_service)

    cli_menu = CLIMenu(
        auth_service=auth_service,
        stock_service=stock_service,
        portfolio_service=portfolio_service,
        transaction_service=transaction_service,
        recommendation_service=recommendation_service,
        report_service=report_service
    )

    try:
        cli_menu.run()
    except KeyboardInterrupt:
        print("\n\nExiting StockVision AI. Goodbye!")

if __name__ == "__main__":
    main()
