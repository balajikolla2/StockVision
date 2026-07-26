"""
services/stock_service.py
Service handling market stocks, inventory, stock lookup, filtering, and Admin stock operations.
"""

from typing import List, Optional, Dict
from storage.file_handler import FileHandler
from models.stock import Stock
from utils import InvalidInputError

class StockService:
    STOCK_HEADERS = ["ticker", "company_name", "price", "sector", "available_quantity", "risk_level", "gainer_pct"]
    STOCKS_FILE = "stocks.txt"

    def __init__(self, file_handler: Optional[FileHandler] = None):
        self.file_handler = file_handler or FileHandler()
        self.file_handler.ensure_file_exists(self.STOCKS_FILE, self.STOCK_HEADERS)

    def get_all_stocks(self) -> List[Stock]:
        """Returns list of all stocks available in the market."""
        records = self.file_handler.read_records(self.STOCKS_FILE)
        return [Stock.from_dict(r) for r in records]

    def get_stock(self, ticker: str) -> Optional[Stock]:
        """Looks up a stock by ticker symbol (case-insensitive)."""
        ticker_clean = ticker.upper().strip()
        stocks = self.get_all_stocks()
        for s in stocks:
            if s.ticker == ticker_clean:
                return s
        return None

    def search_stocks(self, query: str) -> List[Stock]:
        """Searches stocks by ticker or company name substring."""
        query = query.lower().strip()
        stocks = self.get_all_stocks()
        return [s for s in stocks if query in s.ticker.lower() or query in s.company_name.lower() or query in s.sector.lower()]

    def filter_stocks_by_sector(self, sector: str) -> List[Stock]:
        """Filters stocks by sector."""
        sector = sector.lower().strip()
        return [s for s in self.get_all_stocks() if s.sector.lower() == sector]

    def filter_stocks_by_risk(self, risk_level: str) -> List[Stock]:
        """Filters stocks by risk level (Low/Medium/High)."""
        risk = risk_level.lower().strip()
        return [s for s in self.get_all_stocks() if s.risk_level.lower() == risk]

    def save_stock(self, stock: Stock) -> bool:
        """Saves a new stock or updates an existing stock record in stocks.txt."""
        stocks = self.get_all_stocks()
        found = False
        updated_stocks = []

        for s in stocks:
            if s.ticker == stock.ticker:
                updated_stocks.append(stock)
                found = True
            else:
                updated_stocks.append(s)

        if not found:
            updated_stocks.append(stock)

        records = [s.to_dict() for s in updated_stocks]
        return self.file_handler.write_records(self.STOCKS_FILE, self.STOCK_HEADERS, records)

    def add_stock(self, ticker: str, company_name: str, price: float, sector: str, 
                  quantity: int, risk_level: str = "Medium", gainer_pct: float = 0.0) -> Stock:
        """
        Admin method to add a new stock to the market catalog.
        """
        ticker = ticker.upper().strip()
        if self.get_stock(ticker):
            raise InvalidInputError(f"Stock with ticker '{ticker}' already exists in market.")

        stock = Stock(
            ticker=ticker,
            company_name=company_name,
            price=price,
            sector=sector,
            available_quantity=quantity,
            risk_level=risk_level,
            gainer_pct=gainer_pct
        )
        self.save_stock(stock)
        return stock

    def update_stock_price(self, ticker: str, new_price: float, new_gainer_pct: Optional[float] = None) -> Stock:
        """
        Admin method to update stock market price and gain percentage.
        """
        stock = self.get_stock(ticker)
        if not stock:
            raise InvalidInputError(f"Stock ticker '{ticker}' not found.")
        
        if new_price <= 0:
            raise InvalidInputError("Stock price must be greater than zero.")

        if new_gainer_pct is None:
            # Calculate gainer percentage based on old price vs new price
            new_gainer_pct = ((new_price - stock.price) / stock.price) * 100

        stock.price = new_price
        stock.gainer_pct = new_gainer_pct
        self.save_stock(stock)
        return stock

    def update_stock_quantity(self, ticker: str, quantity_change: int) -> Stock:
        """
        Updates stock inventory quantity. Positive to increase supply, negative to decrease.
        """
        stock = self.get_stock(ticker)
        if not stock:
            raise InvalidInputError(f"Stock ticker '{ticker}' not found.")

        new_qty = stock.available_quantity + quantity_change
        if new_qty < 0:
            raise InvalidInputError(f"Cannot reduce stock supply below 0 (current: {stock.available_quantity}).")

        stock.available_quantity = new_qty
        self.save_stock(stock)
        return stock
