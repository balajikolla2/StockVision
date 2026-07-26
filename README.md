# StockVision AI - Stock Market & Portfolio Management Engine

**StockVision AI** is a modular, Object-Oriented Programming (OOP) CLI application built in **Python 3.13**. It provides a role-based environment for **Investors** to manage wallets, trade stocks, analyze portfolios, get AI recommendations, and generate financial reports, while enabling **Administrators** to oversee stock market listings, manage inventory, track transactions, and view market-wide analytics.

---

## Technical Stack

- **Core**: Python 3.13
- **Paradigm**: Object-Oriented Programming (Inheritance, Polymorphism, Encapsulation, Abstraction)
- **Data Persistence**: File Handling (`.txt` files with pipe `|` delimitation)
- **Error Handling**: Custom exception hierarchy with input & data integrity validation
- **Architecture**: Modular Layered Architecture (Models, Services, Storage, CLI Menu)

---

## Role-Based Architecture

### 1. Administrator Role (`admin`)
- **Market Management**: Add new stocks, update stock market prices, adjust stock share supply inventory.
- **User Auditing**: View all registered system users (Admins & Investors) and their account details.
- **Transaction Logs**: Monitor system-wide trading transaction records in real time.
- **Market Analytics**: Generate comprehensive reports on total market cap, inventory volume, and trading activity.

### 2. Investor Role (`investor`)
- **Market Browsing & Search**: Search stocks by ticker, company name, sector, or risk appetite.
- **Trading Engine**: Buy and sell stock shares with real-time wallet deduction and stock inventory updates.
- **Portfolio Analytics**: Track active stock positions, cost basis, current market value, unrealized profit/loss, and ROI %.
- **Wallet Operations**: Deposit and withdraw funds with balance safety checks.
- **AI Recommendation Engine**: Receive tailored stock suggestions based on risk preference, wallet budget, and stock performance.
- **Financial Performance Report**: View detailed financial summary reports.

---

## Directory Structure

```
StockVision_AI/
│
├── main.py                    # Application Entry Point & Data Seeder
├── menu.py                    # Role-Based CLI Menu & Event Handlers
├── utils.py                   # Custom Exceptions, Password Hashing & Validators
├── login.py                   # AuthService, Registration & Session State
│
├── models/                    # Domain Data Models (OOP)
│   ├── user.py                # Abstract Base User Class
│   ├── admin.py               # Admin Model (Inherits User)
│   ├── investor.py            # Investor Model (Inherits User)
│   ├── stock.py               # Stock Model
│   ├── portfolio.py           # Portfolio & Holding Models
│   └── wallet.py              # Wallet Financial Model
│
├── services/                  # Business Logic Layer
│   ├── stock_service.py       # Stock Catalog & Admin Catalog Updates
│   ├── portfolio_service.py   # Trade Execution (Buy/Sell) & Portfolio State
│   ├── recommendation.py      # AI Algorithmic Stock Recommender
│   ├── report_service.py      # Performance & Analytics Report Generator
│   └── transaction_service.py # Transaction Logging & Audit History
│
├── storage/                   # Data Storage Layer
│   └── file_handler.py        # Generic & Entity Pipe-Delimited File Handler
│
├── data/                      # Persistent Text Storage (.txt)
│   ├── users.txt              # User Accounts (Hashed Passwords, Roles, Balances)
│   ├── stocks.txt             # Stock Market Listings & Inventory
│   ├── portfolio.txt          # Active Investor Holdings
│   └── transactions.txt       # Historical Audit Log
│
└── README.md                  # System Documentation
```

---

## Quick Start & Execution

### Running the Application

Navigate to the project root directory and execute `main.py`:

```bash
cd StockVision_AI
python main.py
```

---

## Default Pre-Seeded Test Credentials

On initial launch, default test accounts and stock market listings are auto-created:

### Administrator Account
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: `admin`

### Pre-Seeded Investor Accounts
1. **Username**: `john_investor`
   - **Password**: `investor123`
   - **Role**: `investor`
   - **Initial Wallet**: `$10,000.00`
   - **Risk Appetite**: `Medium`

2. **Username**: `sarah_trader`
   - **Password**: `investor123`
   - **Role**: `investor`
   - **Initial Wallet**: `$25,000.00`
   - **Risk Appetite**: `High`
