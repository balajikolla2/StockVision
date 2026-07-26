"""
models/admin.py
Admin class inheriting from User. Represents system administrators with market management permissions.
"""

from models.user import User

class Admin(User):
    def __init__(self, user_id: str, username: str, password_hash: str, email: str):
        super().__init__(user_id, username, password_hash, email, role="admin")

    def get_dashboard_type(self) -> str:
        return "Administrator Dashboard"

    def is_admin(self) -> bool:
        return True

    def __repr__(self) -> str:
        return f"Admin(id={self.user_id}, username='{self.username}')"
