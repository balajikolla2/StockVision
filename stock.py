"""
models/stock.py
Stock model representing a tradeable equity security in StockVision AI.
"""

from typing import Dict

class Stock:
    def __init__(self, ticker: str, company_name: str, price: float, sector: str, 
                 available_quantity: int, risk_level: str = "Medium", gainer_pct: float = 0.0):
        self.ticker = ticker.upper().strip()
        self.company_name = company_name.strip()
        self.price = float(price)
        self.sector = sector.strip().title()
        self.available_quantity = int(available_quantity)
        self.risk_level = risk_level.strip().capitalize()
        self.gainer_pct = float(gainer_pct)

    def to_dict(self) -> Dict[str, str]:
        return {
            "ticker": self.ticker,
            "company_name": self.company_name,
            "price": f"{self.price:.2f}",
            "sector": self.sector,
            "available_quantity": str(self.available_quantity),
            "risk_level": self.risk_level,
            "gainer_pct": f"{self.gainer_pct:.2f}"
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Stock":
        return cls(
            ticker=data.get("ticker", ""),
            company_name=data.get("company_name", ""),
            price=float(data.get("price", 0.0)),
            sector=data.get("sector", "General"),
            available_quantity=int(data.get("available_quantity", 0)),
            risk_level=data.get("risk_level", "Medium"),
            gainer_pct=float(data.get("gainer_pct", 0.0))
        )

    def __repr__(self) -> str:
        return f"Stock({self.ticker}: ${self.price:.2f}, Qty={self.available_quantity}, Sector={self.sector})"
