"""
models/user.py
Base class representing a user in the StockVision AI system.
"""

from abc import ABC, abstractmethod
from typing import Dict

class User(ABC):
    def __init__(self, user_id: str, username: str, password_hash: str, email: str, role: str):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.role = role.lower()

    @abstractmethod
    def get_dashboard_type(self) -> str:
        """Returns the dashboard title/type associated with the user's role."""
        pass

    def to_dict(self) -> Dict[str, str]:
        """Serializes user object to dictionary for storage."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "password_hash": self.password_hash,
            "email": self.email,
            "role": self.role
        }

    def __repr__(self) -> str:
        return f"User(id={self.user_id}, username='{self.username}', role='{self.role}')"
