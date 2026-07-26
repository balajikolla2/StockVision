"""
login.py
Authentication Service module handling user registration, authentication, role verification, and session state.
"""

from typing import Optional, Dict
import uuid
from storage.file_handler import FileHandler
from models.user import User
from models.admin import Admin
from models.investor import Investor
from utils import (
    hash_password, verify_password, validate_username, 
    validate_password, validate_email, UserAlreadyExistsError, AuthenticationError
)

class AuthService:
    USER_HEADERS = ["user_id", "username", "password_hash", "email", "role", "balance", "risk_preference"]
    USERS_FILE = "users.txt"

    def __init__(self, file_handler: Optional[FileHandler] = None):
        self.file_handler = file_handler or FileHandler()
        self.file_handler.ensure_file_exists(self.USERS_FILE, self.USER_HEADERS)
        self.current_user: Optional[User] = None

    def register_investor(self, username: str, password: str, email: str, 
                          initial_deposit: float = 1000.0, risk_preference: str = "Medium") -> Investor:
        """
        Registers a new Investor account.
        Validates inputs, checks for existing username, hashes password, and saves user record.
        """
        clean_username = validate_username(username)
        clean_password = validate_password(password)
        clean_email = validate_email(email)

        # Check if username already exists
        existing_users = self.file_handler.read_records(self.USERS_FILE)
        for u in existing_users:
            if u.get("username", "").lower() == clean_username.lower():
                raise UserAlreadyExistsError(f"Username '{clean_username}' is already taken.")

        user_id = f"USR-{uuid.uuid4().hex[:6].upper()}"
        pwd_hash = hash_password(clean_password)
        
        investor = Investor(
            user_id=user_id,
            username=clean_username,
            password_hash=pwd_hash,
            email=clean_email,
            wallet_balance=initial_deposit,
            risk_preference=risk_preference
        )

        # Persist to users.txt
        record = {
            "user_id": investor.user_id,
            "username": investor.username,
            "password_hash": investor.password_hash,
            "email": investor.email,
            "role": investor.role,
            "balance": f"{investor.wallet.balance:.2f}",
            "risk_preference": investor.risk_preference
        }
        self.file_handler.append_record(self.USERS_FILE, self.USER_HEADERS, record)

        return investor

    def login(self, username: str, password: str) -> User:
        """
        Authenticates a user by username and password.
        Loads role-specific model (Admin or Investor) into current session.
        """
        username = username.strip()
        records = self.file_handler.read_records(self.USERS_FILE)
        
        user_record: Optional[Dict[str, str]] = None
        for r in records:
            if r.get("username", "").lower() == username.lower():
                user_record = r
                break

        if not user_record:
            raise AuthenticationError("Invalid username or password.")

        if not verify_password(password, user_record.get("password_hash", "")):
            raise AuthenticationError("Invalid username or password.")

        # Reconstruct object based on role (OOP Polymorphism)
        role = user_record.get("role", "investor").lower()
        if role == "admin":
            user = Admin(
                user_id=user_record.get("user_id", ""),
                username=user_record.get("username", ""),
                password_hash=user_record.get("password_hash", ""),
                email=user_record.get("email", "")
            )
        else:
            balance = float(user_record.get("balance", "0.0"))
            risk_pref = user_record.get("risk_preference", "Medium")
            user = Investor(
                user_id=user_record.get("user_id", ""),
                username=user_record.get("username", ""),
                password_hash=user_record.get("password_hash", ""),
                email=user_record.get("email", ""),
                wallet_balance=balance,
                risk_preference=risk_pref
            )

        self.current_user = user
        return user

    def logout(self) -> None:
        """Logs out the active user session."""
        self.current_user = None

    def update_user_record(self, user: User) -> bool:
        """
        Persists updated user state (e.g. changed wallet balance or email) to storage.
        """
        records = self.file_handler.read_records(self.USERS_FILE)
        updated_records = []

        for r in records:
            if r.get("user_id") == user.user_id:
                if isinstance(user, Investor):
                    r["balance"] = f"{user.wallet.balance:.2f}"
                    r["risk_preference"] = user.risk_preference
                r["email"] = user.email
            updated_records.append(r)

        return self.file_handler.write_records(self.USERS_FILE, self.USER_HEADERS, updated_records)
