"""
menu.py
Role-based CLI Menu Interface for StockVision AI.
Provides distinct interactive menus and action handlers for Investors and Admins.
"""

from typing import Optional
from login import AuthService
from services.stock_service import StockService
from services.portfolio_service import PortfolioService
from services.transaction_service import TransactionService
from services.recommendation import RecommendationService
from services.report_service import ReportService
from models.admin import Admin
from models.investor import Investor
from utils import (
    print_header, print_subheader, format_currency, format_percentage,
    validate_positive_float, validate_positive_int,
    StockVisionException, InsufficientFundsError, InsufficientStockError
)

class CLIMenu:
    def __init__(self, auth_service: AuthService,
                 stock_service: StockService,
                 portfolio_service: PortfolioService,
                 transaction_service: TransactionService,
                 recommendation_service: RecommendationService,
                 report_service: ReportService):
        self.auth_service = auth_service
        self.stock_service = stock_service
        self.portfolio_service = portfolio_service
        self.transaction_service = transaction_service
        self.recommendation_service = recommendation_service
        self.report_service = report_service

    # =========================================================================
    # MAIN CLI ENTRY POINT & ROLE ROUTING
    # =========================================================================

    def run(self) -> None:
        """Main application execution loop."""
        while True:
            if not self.auth_service.current_user:
                self._show_auth_menu()
            else:
                user = self.auth_service.current_user
                if isinstance(user, Admin):
                    self._show_admin_menu(user)
                elif isinstance(user, Investor):
                    self._show_investor_menu(user)

    # =========================================================================
    # AUTHENTICATION MENU (GUEST / WELCOME)
    # =========================================================================

    def _show_auth_menu(self) -> None:
        print_header("WELCOME TO STOCKVISION AI - STOCK MARKET ENGINE")
        print(" [1] Login to Account")
        print(" [2] Register New Investor Account")
        print(" [3] View Public Market Overview")
        print(" [0] Exit Application")
        print("-" * 60)

        choice = input("Enter choice (0-3): ").strip()
        if choice == "1":
            self._handle_login()
        elif choice == "2":
            self._handle_registration()
        elif choice == "3":
            self._view_stock_catalog()
        elif choice == "0":
            print("\nThank you for using StockVision AI. Goodbye!")
            exit(0)
        else:
            print("\n[!] Invalid choice. Please try again.")

    def _handle_login(self) -> None:
        print_subheader("USER LOGIN")
        username = input("Username: ").strip()
        password = input("Password: ").strip()

        try:
            user = self.auth_service.login(username, password)
            print(f"\n[+] Login successful! Welcome back, {user.username} ({user.get_dashboard_type()}).")
        except StockVisionException as e:
            print(f"\n[!] Authentication Error: {e}")

    def _handle_registration(self) -> None:
        print_subheader("INVESTOR ACCOUNT REGISTRATION")
        username = input("Choose Username (3-20 chars): ").strip()
        password = input("Choose Password (min 6 chars): ").strip()
        email = input("Email Address: ").strip()
        
        print("\nSelect Risk Appetite Preference:")
        print(" 1. Low Risk (Prefers stable dividend/large-cap stocks)")
        print(" 2. Medium Risk (Balanced portfolio)")
        print(" 3. High Risk (Growth & volatile stocks)")
        risk_choice = input("Choice (1-3) [Default 2]: ").strip()
        risk_map = {"1": "Low", "2": "Medium", "3": "High"}
        risk_pref = risk_map.get(risk_choice, "Medium")

        initial_deposit_str = input("Initial Wallet Deposit Amount ($) [Default $1,000]: ").strip()
        deposit = 1000.0
        if initial_deposit_str:
            try:
                deposit = validate_positive_float(initial_deposit_str, "Initial Deposit")
            except StockVisionException as e:
                print(f"\n[!] Registration Error: {e}")
                return

        try:
            investor = self.auth_service.register_investor(
                username=username,
                password=password,
                email=email,
                initial_deposit=deposit,
                risk_preference=risk_pref
            )
            print(f"\n[+] Investor account '{investor.username}' registered successfully!")
            print(f"    Initial wallet balance: {format_currency(investor.wallet.balance)}")
            print("    Please login with your new credentials.")
        except StockVisionException as e:
            print(f"\n[!] Registration Failed: {e}")

    # =========================================================================
    # ROLE: INVESTOR DASHBOARD & ACTIONS
    # =========================================================================

    def _show_investor_menu(self, investor: Investor) -> None:
        print_header(f"INVESTOR DASHBOARD - WELCOME {investor.username.upper()}")
        print(f" Wallet Balance: {format_currency(investor.wallet.balance)}  |  Risk Appetite: {investor.risk_preference}")
        print("-" * 60)
        print(" [1]  Browse Market Stocks")
        print(" [2]  Search / Filter Stocks")
        print(" [3]  Buy Stock Shares")
        print(" [4]  Sell Stock Shares")
        print(" [5]  View My Portfolio & Performance")
        print(" [6]  Wallet Operations (Deposit / Withdraw)")
        print(" [7]  My Transaction History")
        print(" [8]  Get AI Smart Stock Recommendations")
        print(" [9]  Generate Investor Financial Report")
        print(" [0]  Logout")
        print("-" * 60)

        choice = input("Enter choice (0-9): ").strip()
        if choice == "1":
            self._view_stock_catalog()
        elif choice == "2":
            self._search_and_filter_stocks()
        elif choice == "3":
            self._investor_buy_stock(investor)
        elif choice == "4":
            self._investor_sell_stock(investor)
        elif choice == "5":
            self._view_investor_portfolio(investor)
        elif choice == "6":
            self._wallet_operations(investor)
        elif choice == "7":
            self._view_user_transaction_history(investor)
        elif choice == "8":
            self._show_ai_recommendations(investor)
        elif choice == "9":
            self._show_investor_report(investor)
        elif choice == "0":
            self.auth_service.logout()
            print("\n[+] Logged out successfully.")
        else:
            print("\n[!] Invalid choice. Please try again.")

    def _view_stock_catalog(self) -> None:
        print_subheader("CURRENT STOCK MARKET LISTINGS")
        stocks = self.stock_service.get_all_stocks()
        if not stocks:
            print("No stock listings found in the market catalog.")
            return

        print(f"{'Ticker':<8} {'Company Name':<22} {'Price':<12} {'Change':<10} {'Available':<12} {'Risk':<8} {'Sector':<15}")
        print("-" * 90)
        for s in stocks:
            change_str = format_percentage(s.gainer_pct)
            print(f"{s.ticker:<8} {s.company_name[:20]:<22} {format_currency(s.price):<12} {change_str:<10} {s.available_quantity:<12} {s.risk_level:<8} {s.sector:<15}")
        print("-" * 90)

    def _search_and_filter_stocks(self) -> None:
        print_subheader("SEARCH & FILTER STOCKS")
        print(" 1. Search by Name / Ticker / Sector")
        print(" 2. Filter by Risk Level (Low / Medium / High)")
        print(" 3. Filter by Sector")
        choice = input("Choice (1-3): ").strip()

        if choice == "1":
            query = input("Enter search query: ").strip()
            results = self.stock_service.search_stocks(query)
        elif choice == "2":
            risk = input("Enter Risk Level (Low/Medium/High): ").strip()
            results = self.stock_service.filter_stocks_by_risk(risk)
        elif choice == "3":
            sector = input("Enter Sector Name (e.g. Tech, Finance, Energy): ").strip()
            results = self.stock_service.filter_stocks_by_sector(sector)
        else:
            print("[!] Invalid filter selection.")
            return

        if not results:
            print("\nNo stocks matched your search criteria.")
            return

        print(f"\nMatching Results ({len(results)} stocks):")
        print(f"{'Ticker':<8} {'Company Name':<22} {'Price':<12} {'Available':<12} {'Risk':<8} {'Sector':<15}")
        print("-" * 80)
        for s in results:
            print(f"{s.ticker:<8} {s.company_name[:20]:<22} {format_currency(s.price):<12} {s.available_quantity:<12} {s.risk_level:<8} {s.sector:<15}")

    def _investor_buy_stock(self, investor: Investor) -> None:
        print_subheader("BUY STOCK SHARES")
        ticker = input("Enter Stock Ticker (e.g., AAPL): ").strip()
        stock = self.stock_service.get_stock(ticker)
        if not stock:
            print(f"[!] Stock '{ticker}' not found in market catalog.")
            return

        print(f"Selected: {stock.ticker} - {stock.company_name}")
        print(f"Current Price: {format_currency(stock.price)} | Available Supply: {stock.available_quantity} shares")
        print(f"Your Wallet Balance: {format_currency(investor.wallet.balance)}")

        qty_str = input("Enter number of shares to buy: ").strip()
        try:
            qty = validate_positive_int(qty_str, "Share Quantity")
            txn = self.portfolio_service.buy_stock(investor, ticker, qty)
            total_cost = float(txn['total_amount'])
            print(f"\n[+] SUCCESS: Bought {qty} shares of {stock.ticker} for {format_currency(total_cost)}!")
            print(f"    New Wallet Balance: {format_currency(investor.wallet.balance)}")
        except StockVisionException as e:
            print(f"\n[!] Trade Failed: {e}")

    def _investor_sell_stock(self, investor: Investor) -> None:
        print_subheader("SELL STOCK SHARES")
        portfolio = self.portfolio_service.load_portfolio(investor)
        holdings = portfolio.get_all_holdings()

        if not holdings:
            print("You currently do not own any stocks to sell.")
            return

        print("Your Current Holdings:")
        print(f"{'Ticker':<8} {'Quantity Owned':<16} {'Avg Buy Price':<14} {'Total Invested':<14}")
        print("-" * 60)
        for h in holdings:
            print(f"{h.ticker:<8} {h.quantity:<16} {format_currency(h.avg_buy_price):<14} {format_currency(h.total_invested):<14}")
        print("-" * 60)

        ticker = input("Enter Ticker of stock to sell: ").strip()
        qty_str = input("Enter number of shares to sell: ").strip()

        try:
            qty = validate_positive_int(qty_str, "Share Quantity")
            txn = self.portfolio_service.sell_stock(investor, ticker, qty)
            proceeds = float(txn['total_amount'])
            print(f"\n[+] SUCCESS: Sold {qty} shares of {ticker.upper()} for {format_currency(proceeds)}!")
            print(f"    New Wallet Balance: {format_currency(investor.wallet.balance)}")
        except StockVisionException as e:
            print(f"\n[!] Sale Failed: {e}")

    def _view_investor_portfolio(self, investor: Investor) -> None:
        print_subheader(f"PORTFOLIO HOLDINGS - {investor.username.upper()}")
        rpt = self.report_service.generate_investor_report(investor)

        print(f" Wallet Balance:       {format_currency(rpt['cash_balance'])}")
        print(f" Total Invested Capital:{format_currency(rpt['total_invested'])}")
        print(f" Current Market Value:  {format_currency(rpt['total_market_value'])}")
        print(f" Combined Net Worth:    {format_currency(rpt['net_worth'])}")
        
        pnl = rpt['total_pnl']
        pnl_str = format_currency(pnl)
        roi_str = format_percentage(rpt['overall_roi'])
        sign = "+" if pnl > 0 else ""
        print(f" Unrealized P&L:        {sign}{pnl_str} ({roi_str})")
        print("-" * 80)

        holdings = rpt['holdings']
        if not holdings:
            print("No active stock positions in portfolio.")
            return

        print(f"{'Ticker':<8} {'Shares':<8} {'Avg Cost':<12} {'Curr Price':<12} {'Market Val':<14} {'P&L ($)':<12} {'ROI (%)':<10}")
        print("-" * 80)
        for h in holdings:
            pnl_val_str = f"{'+' if h['pnl']>0 else ''}{format_currency(h['pnl'])}"
            print(f"{h['ticker']:<8} {h['quantity']:<8} {format_currency(h['avg_buy_price']):<12} {format_currency(h['current_price']):<12} {format_currency(h['market_value']):<14} {pnl_val_str:<12} {format_percentage(h['roi_pct']):<10}")
        print("-" * 80)

    def _wallet_operations(self, investor: Investor) -> None:
        print_subheader("WALLET MANAGEMENT")
        print(f" Current Available Balance: {format_currency(investor.wallet.balance)}")
        print(" 1. Deposit Funds")
        print(" 2. Withdraw Funds")
        print(" 0. Back")

        choice = input("Choice (0-2): ").strip()
        if choice == "1":
            val = input("Enter deposit amount ($): ").strip()
            try:
                amt = validate_positive_float(val, "Deposit Amount")
                investor.wallet.deposit(amt)
                self.auth_service.update_user_record(investor)
                print(f"\n[+] Deposited {format_currency(amt)} successfully! New Balance: {format_currency(investor.wallet.balance)}")
            except StockVisionException as e:
                print(f"[!] Deposit Error: {e}")
        elif choice == "2":
            val = input("Enter withdrawal amount ($): ").strip()
            try:
                amt = validate_positive_float(val, "Withdrawal Amount")
                investor.wallet.withdraw(amt)
                self.auth_service.update_user_record(investor)
                print(f"\n[+] Withdrew {format_currency(amt)} successfully! New Balance: {format_currency(investor.wallet.balance)}")
            except StockVisionException as e:
                print(f"[!] Withdrawal Error: {e}")

    def _view_user_transaction_history(self, investor: Investor) -> None:
        print_subheader("TRANSACTION HISTORY LOG")
        txns = self.transaction_service.get_user_transactions(investor.user_id)
        if not txns:
            print("No past transaction records found.")
            return

        print(f"{'Txn ID':<14} {'Timestamp':<20} {'Type':<6} {'Ticker':<8} {'Qty':<6} {'Price':<10} {'Total ($)':<12}")
        print("-" * 80)
        for t in reversed(txns):
            print(f"{t.get('transaction_id'):<14} {t.get('timestamp'):<20} {t.get('type'):<6} {t.get('ticker'):<8} {t.get('quantity'):<6} ${float(t.get('price',0)):<9.2f} ${float(t.get('total_amount',0)):<11.2f}")

    def _show_ai_recommendations(self, investor: Investor) -> None:
        print_subheader("AI ALGORITHMIC STOCK RECOMMENDATIONS")
        recs = self.recommendation_service.get_recommendations_for_investor(investor, limit=5)

        if not recs:
            print("No recommendations available at this time.")
            return

        print(f"Tailored for Risk Preference: {investor.risk_preference} | Available Balance: {format_currency(investor.wallet.balance)}\n")
        print(f"{'Rank':<5} {'Ticker':<8} {'Company Name':<22} {'Price':<12} {'Risk':<8} {'Recommendation Reason':<35}")
        print("-" * 95)
        for idx, item in enumerate(recs, 1):
            s = item['stock']
            print(f"#{idx:<4} {s.ticker:<8} {s.company_name[:20]:<22} {format_currency(s.price):<12} {s.risk_level:<8} {item['reason']:<35}")
        print("-" * 95)

    def _show_investor_report(self, investor: Investor) -> None:
        print_subheader("INVESTOR PERFORMANCE & FINANCIAL REPORT")
        rpt = self.report_service.generate_investor_report(investor)

        print(f" Account Holder:   {rpt['investor_name']} ({rpt['email']})")
        print(f" Risk Preference:  {rpt['risk_preference']}")
        print(f" Total Trades:     {rpt['total_trades']} ({rpt['buy_trades']} Buys, {rpt['sell_trades']} Sells)")
        print(f" Cash Balance:     {format_currency(rpt['cash_balance'])}")
        print(f" Portfolio Value:  {format_currency(rpt['total_market_value'])}")
        print(f" Total Net Worth:  {format_currency(rpt['net_worth'])}")
        print(f" Total Net P&L:    {format_currency(rpt['total_pnl'])}")
        print(f" Overall ROI:      {format_percentage(rpt['overall_roi'])}")
        print("-" * 60)

    # =========================================================================
    # ROLE: ADMIN DASHBOARD & ACTIONS
    # =========================================================================

    def _show_admin_menu(self, admin: Admin) -> None:
        print_header(f"ADMINISTRATOR DASHBOARD - WELCOME {admin.username.upper()}")
        print(" SYSTEM MANAGEMENT & CONTROL CENTER")
        print("-" * 60)
        print(" [1] View Market Catalog")
        print(" [2] Add New Stock to Market")
        print(" [3] Update Stock Price & Market Performance")
        print(" [4] Update Stock Available Supply")
        print(" [5] View All Registered System Users")
        print(" [6] View System-Wide Transaction Logs")
        print(" [7] Generate Market Analytics Report")
        print(" [0] Logout")
        print("-" * 60)

        choice = input("Enter choice (0-7): ").strip()
        if choice == "1":
            self._view_stock_catalog()
        elif choice == "2":
            self._admin_add_stock()
        elif choice == "3":
            self._admin_update_price()
        elif choice == "4":
            self._admin_update_supply()
        elif choice == "5":
            self._admin_view_users()
        elif choice == "6":
            self._admin_view_all_transactions()
        elif choice == "7":
            self._admin_market_report()
        elif choice == "0":
            self.auth_service.logout()
            print("\n[+] Admin Logged out successfully.")
        else:
            print("\n[!] Invalid choice. Please try again.")

    def _admin_add_stock(self) -> None:
        print_subheader("ADMIN: ADD NEW STOCK TO MARKET")
        ticker = input("Stock Ticker Symbol (e.g. TSLA): ").strip()
        company = input("Company Name: ").strip()
        price_str = input("Initial Unit Price ($): ").strip()
        sector = input("Sector (Tech, Energy, Healthcare, etc.): ").strip()
        qty_str = input("Initial Available Share Inventory: ").strip()
        risk = input("Risk Level (Low/Medium/High) [Default Medium]: ").strip() or "Medium"

        try:
            price = validate_positive_float(price_str, "Price")
            qty = validate_positive_int(qty_str, "Inventory Quantity")
            stock = self.stock_service.add_stock(ticker, company, price, sector, qty, risk)
            print(f"\n[+] SUCCESS: Stock {stock.ticker} ({stock.company_name}) added to market at {format_currency(stock.price)}!")
        except StockVisionException as e:
            print(f"\n[!] Failed to add stock: {e}")

    def _admin_update_price(self) -> None:
        print_subheader("ADMIN: UPDATE STOCK MARKET PRICE")
        ticker = input("Enter Stock Ticker: ").strip()
        price_str = input("Enter New Price ($): ").strip()

        try:
            new_price = validate_positive_float(price_str, "New Stock Price")
            stock = self.stock_service.update_stock_price(ticker, new_price)
            print(f"\n[+] SUCCESS: Price for {stock.ticker} updated to {format_currency(stock.price)} ({format_percentage(stock.gainer_pct)} change).")
        except StockVisionException as e:
            print(f"\n[!] Failed to update stock price: {e}")

    def _admin_update_supply(self) -> None:
        print_subheader("ADMIN: UPDATE STOCK SUPPLY INVENTORY")
        ticker = input("Enter Stock Ticker: ").strip()
        qty_change_str = input("Quantity adjustment (positive to add supply, negative to reduce): ").strip()

        try:
            qty_change = int(qty_change_str)
            stock = self.stock_service.update_stock_quantity(ticker, qty_change)
            print(f"\n[+] SUCCESS: Supply for {stock.ticker} updated. New available inventory: {stock.available_quantity} shares.")
        except ValueError:
            print("[!] Invalid integer for quantity adjustment.")
        except StockVisionException as e:
            print(f"\n[!] Update Failed: {e}")

    def _admin_view_users(self) -> None:
        print_subheader("ADMIN: SYSTEM USERS LIST")
        users = self.auth_service.file_handler.read_records("users.txt")
        if not users:
            print("No user records found.")
            return

        print(f"{'User ID':<12} {'Username':<18} {'Role':<10} {'Email':<25} {'Balance ($)':<12}")
        print("-" * 80)
        for u in users:
            bal_str = format_currency(float(u.get('balance',0.0))) if u.get('role') == 'investor' else 'N/A'
            print(f"{u.get('user_id'):<12} {u.get('username'):<18} {u.get('role'):<10} {u.get('email'):<25} {bal_str:<12}")

    def _admin_view_all_transactions(self) -> None:
        print_subheader("ADMIN: ALL SYSTEM TRANSACTIONS")
        txns = self.transaction_service.get_all_transactions()
        if not txns:
            print("No transactions recorded in system.")
            return

        print(f"{'Txn ID':<14} {'User ID':<12} {'Timestamp':<20} {'Type':<6} {'Ticker':<8} {'Qty':<6} {'Total ($)':<12}")
        print("-" * 85)
        for t in reversed(txns):
            print(f"{t.get('transaction_id'):<14} {t.get('user_id'):<12} {t.get('timestamp'):<20} {t.get('type'):<6} {t.get('ticker'):<8} {t.get('quantity'):<6} ${float(t.get('total_amount',0)):<11.2f}")

    def _admin_market_report(self) -> None:
        print_subheader("ADMIN: SYSTEM-WIDE MARKET ANALYTICS REPORT")
        rpt = self.report_service.generate_admin_report()

        print(f" Registered System Users: {rpt['total_users']} ({rpt['investor_count']} Investors, {rpt['admin_count']} Admins)")
        print(f" Stocks Listed in Market: {rpt['total_stocks_listed']}")
        print(f" Total Shares Inventory:  {rpt['total_shares_available']:,} shares")
        print(f" Total Market Cap:        {format_currency(rpt['market_cap'])}")
        print(f" Total Transactions Logged:{rpt['total_transactions']}")
        print(f" Cumulative Trade Volume: {format_currency(rpt['total_trading_volume'])}")
        print("-" * 60)
