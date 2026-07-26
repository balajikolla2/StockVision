"""
services/recommendation.py
Smart AI Stock Recommendation Service providing tailored investment suggestions.
"""

from typing import List, Dict, Optional
from models.investor import Investor
from models.stock import Stock
from services.stock_service import StockService

class RecommendationService:
    def __init__(self, stock_service: Optional[StockService] = None):
        self.stock_service = stock_service or StockService()

    def get_recommendations_for_investor(self, investor: Investor, limit: int = 5) -> List[Dict]:
        """
        Generates personalized stock recommendations based on:
        - Investor risk preference (Low, Medium, High)
        - Current wallet budget balance
        - Performance (Gainer %) and stock inventory availability
        """
        all_stocks = self.stock_service.get_all_stocks()
        if not all_stocks:
            return []

        user_risk = investor.risk_preference.lower()
        wallet_balance = investor.wallet.balance

        scored_stocks = []
        for stock in all_stocks:
            if stock.available_quantity <= 0:
                continue

            score = 50.0  # Base score

            # 1. Risk Level Matching (+30 points for exact match, +10 for adjacent)
            stock_risk = stock.risk_level.lower()
            if stock_risk == user_risk:
                score += 30.0
            elif (user_risk == "medium") or (user_risk == "low" and stock_risk == "medium") or (user_risk == "high" and stock_risk == "medium"):
                score += 15.0

            # 2. Performance / Gainer Percentage (+1.5x gainer_pct)
            score += stock.gainer_pct * 1.5

            # 3. Affordability factor (+20 points if investor can buy at least 5 shares)
            if stock.price * 5 <= wallet_balance:
                score += 20.0
            elif stock.price <= wallet_balance:
                score += 10.0
            else:
                score -= 25.0  # Cannot afford single share with cash balance

            # Recommendation reason generation
            reason_parts = []
            if stock_risk == user_risk:
                reason_parts.append(f"Matches your {investor.risk_preference} risk profile")
            if stock.gainer_pct > 2.0:
                reason_parts.append(f"Strong performance (+{stock.gainer_pct:.1f}%)")
            if stock.price * 5 <= wallet_balance:
                reason_parts.append("Highly affordable for your current wallet balance")

            reason = "; ".join(reason_parts) if reason_parts else "Good overall market valuation"

            scored_stocks.append({
                "stock": stock,
                "score": score,
                "reason": reason
            })

        # Sort by recommendation score descending
        scored_stocks.sort(key=lambda x: x["score"], reverse=True)
        return scored_stocks[:limit]

    def get_top_gainers(self, limit: int = 5) -> List[Stock]:
        """Returns top gaining stocks sorted by gain percentage."""
        stocks = self.stock_service.get_all_stocks()
        stocks.sort(key=lambda s: s.gainer_pct, reverse=True)
        return stocks[:limit]
