"""
utils.py
Utility functions, validation helpers, formatting tools, and custom exception classes.
"""

import hashlib
import re
from typing import Any

# ============================================================================
# CUSTOM EXCEPTION HIERARCHY
# ============================================================================

class StockVisionException(Exception):
    """Base exception for all application errors."""
    pass

class AuthenticationError(StockVisionException):
    """Raised when authentication fails (invalid username, password, or role access)."""
    pass

class UserAlreadyExistsError(StockVisionException):
    """Raised when registering a user with an already existing username."""
    pass

class InsufficientFundsError(StockVisionException):
    """Raised when an investor has insufficient wallet funds for a trade or withdrawal."""
    pass

class InsufficientStockError(StockVisionException):
    """Raised when attempting to purchase or sell more stock shares than available."""
    pass

class InvalidInputError(StockVisionException):
    """Raised when user input validation fails."""
    pass

class DataStorageError(StockVisionException):
    """Raised when reading or writing data storage fails."""
    pass

class UnauthorizedRoleError(StockVisionException):
    """Raised when a user attempts an action restricted to a different role."""
    pass


# ============================================================================
# SECURITY & HASHING UTILITIES
# ============================================================================

def hash_password(password: str) -> str:
    """Returns SHA-256 hex digest of the password."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain text password against SHA-256 hash."""
    return hash_password(plain_password) == hashed_password


# ============================================================================
# INPUT VALIDATION HELPERS
# ============================================================================

def validate_username(username: str) -> str:
    """Validates username (alphanumeric & underscore, length 3-20)."""
    username = username.strip()
    if not username:
        raise InvalidInputError("Username cannot be empty.")
    if not re.match(r"^[a-zA-Z0-9_]{3,20}$", username):
        raise InvalidInputError("Username must be 3-20 characters long and contain only letters, numbers, or underscores.")
    return username

def validate_password(password: str) -> str:
    """Validates password strength (minimum 6 characters)."""
    if len(password) < 6:
        raise InvalidInputError("Password must be at least 6 characters long.")
    return password

def validate_email(email: str) -> str:
    """Validates email format."""
    email = email.strip()
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(pattern, email):
        raise InvalidInputError("Invalid email format (e.g. user@example.com).")
    return email

def validate_positive_float(val: str, field_name: str = "Amount") -> float:
    """Parses and validates a positive float number."""
    try:
        amount = float(val.strip())
        if amount <= 0:
            raise InvalidInputError(f"{field_name} must be greater than 0.")
        return amount
    except ValueError:
        raise InvalidInputError(f"Invalid numeric input for {field_name}.")

def validate_positive_int(val: str, field_name: str = "Quantity") -> int:
    """Parses and validates a positive integer."""
    try:
        qty = int(val.strip())
        if qty <= 0:
            raise InvalidInputError(f"{field_name} must be greater than 0.")
        return qty
    except ValueError:
        raise InvalidInputError(f"Invalid integer input for {field_name}.")


# ============================================================================
# FORMATTING & DISPLAY UTILITIES
# ============================================================================

def format_currency(amount: float) -> str:
    """Formats float as USD currency ($1,234.56)."""
    return f"${amount:,.2f}"

def format_percentage(val: float) -> str:
    """Formats float as percentage (+5.25% / -3.10%)."""
    sign = "+" if val > 0 else ""
    return f"{sign}{val:.2f}%"

def print_header(title: str, width: int = 60) -> None:
    """Prints a styled header bar."""
    print("\n" + "=" * width)
    print(f" {title.upper().center(width - 2)} ")
    print("=" * width)

def print_subheader(title: str, width: int = 60) -> None:
    """Prints a secondary header bar."""
    print("-" * width)
    print(f" {title} ")
    print("-" * width)
