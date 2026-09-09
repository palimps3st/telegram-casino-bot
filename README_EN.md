<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/aiogram-3.x-26A5E4?style=for-the-badge&logo=telegram" />
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0-FCA121?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />
</p>

<h1 align="center">🎰 Telegram Casino Bot</h1>
<p align="center">
  <b>Asynchronous casino bot for Telegram</b><br>
  6 games • Deposits & Withdrawals • Admin panel • Bonus roulette
</p>

---

## 🎬 Demo

See it in action:

https://github.com/user-attachments/assets/cc5d13cd-418b-4c09-8152-2efce983ede9

---

## ✨ palimps3st

### 🎮 Games
| Game | Description |
|------|----------|
| 🎰 **Slots** | Classic 3-reel slots with multipliers. 3 in a row gives the maximum win! |
| 🃏 **Blackjack** | Play against the dealer. Hit or stand. Instant Blackjack = x2.5 |
| 💣 **Mines** | Open cells on a 5×5 field, avoid mines. Cash out your winnings at any time. |
| 🚀 **Crash (Rocket)** | Watch the multiplier grow. Cash out before the crash or set a target multiplier. |
| 🎲 **Even / Odd** | Guess the parity of a number from 1 to 100. 1:1 payout. |
| 🎡 **Roulette** | Bet on a specific number (x35), color (x1), or range (x2). |

### 💰 Finances
- **Deposits** — select the amount with transfer details provided (USDT TRC20 / others).
- **Withdrawals** — request from 1000 ₽ by providing your details. Admins get notified via Telegram.

### 🎁 Bonuses
- **Daily Roulette** — spin once every 24 hours and get from +10% up to double your balance.

### 🛡️ Admin Panel
| Command | Description |
|---------|----------|
| 📢 Broadcast | Send HTML broadcasts to all users |
| ➕ Add balance | Top up any user's balance by their ID |
| 🚫 Block / ✅ Unblock | Block a user with a notification sent to the player |
| 📊 Statistics | User count, deposits, withdrawals/purchases, total balance |
| 🔧 Rigging | Change the multiplier (odds) for any game |

### 🔒 Security
- Block check on **all** events (messages + inline buttons).
- Automatic user creation upon first `/start`.
- Bet deduction **before** the game starts — no "hanging" bets.

---

## 🚀 Installation & Launch

### 1. Clone the repository
```bash
git clone https://github.com/A-R-E-S/telegram-casino-bot.git
cd telegram-casino-bot
```

### 2. Install dependencies
It is recommended to use a virtual environment (`venv`):
```bash
python -m venv venv
source venv/bin/activate  # For Linux/Mac
# venv\Scripts\activate   # For Windows

pip install aiogram sqlalchemy aiosqlite bcrypt
```

### 3. Configuration
Open the `settings.py` file and fill in the basic variables:
```python
BOT_TOKEN = "123456:ABC-DEF..."          # Token from @BotFather
ADMINS = [123456789]                     # Telegram IDs of administrators
TECH_SUPPORT_USER_ID = 123456789         # Tech support ID (where requests go)
```

### 4. Run the bot
```bash
python main.py
```

---

## 📁 Project Structure

```text
tg-bot/
├── main.py                     # Entry point
├── settings.py                 # Configuration
├── db/
│   ├── database.py             # SQLite connection
│   └── models.py               # SQLAlchemy models
├── bot/
│   ├── keyboards.py            # Reply/Inline keyboards
│   ├── middlewares/
│   │   └── block_check.py      # Block check middleware
│   └── handlers/
│       ├── auth.py             # Auto-registration
│       ├── profile.py          # User profile
│       ├── common.py           # "Back" button
│       ├── top_up.py           # Deposits and withdrawals
│       ├── support.py          # Tech support
│       ├── bonuses.py          # Bonus roulette
│       ├── admin_handlers.py   # Admin panel
│       └── games/
│           ├── games_menu.py   # Games menu
│           ├── slots.py
│           ├── roulette.py
│           ├── blackjack.py
│           ├── mines.py
│           ├── crash.py
│           └── even_odd.py
└── README.md
```

---

## 🛠 Technologies

- **Python 3.10+**
- **aiogram 3.x** — asynchronous framework for Telegram Bot API
- **SQLAlchemy 2.0 + aiosqlite** — asynchronous ORM and SQLite database 
- **aiogram FSM** — state machine for step-by-step processes and games

## 📄 License

This project is licensed under the **MIT** License.
