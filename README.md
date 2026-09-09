<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/aiogram-3.x-26A5E4?style=for-the-badge&logo=telegram" />
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0-FCA121?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />
</p>

<h1 align="center">🎰 Telegram Casino Bot</h1>
<p align="center">
  <b>Асинхронный казино-бот для Telegram</b><br>
  6 игр • Пополнение и вывод • Админ-панель • Бонусная рулетка
</p>

---

## 🎬 Демонстрация

Посмотри, работает как бот:

https://github.com/user-attachments/assets/cc5d13cd-418b-4c09-8152-2efce983ede9

---

## ✨ Возможности

### 🎮 Игры
| Игра | Описание |
|------|----------|
| 🎰 **Слоты** | Классические 3-барабанные слоты с множителями. 3 в ряд — максимальный выигрыш! |
| 🃏 **Blackjack** | Сыграй против дилера. Возьми карту или остановись. Мгновенный Blackjack = x2.5 |
| 💣 **Мины** | Открывай клетки на поле 5×5, избегай мин. Забирай выигрыш в любой момент. |
| 🚀 **Ракета (Crash)** | Следи за ростом множителя. Забери до краха или укажи целевой коэффициент. |
| 🎲 **Чёт / Нечёт** | Угадай чётность числа от 1 до 100. Выплата 1:1. |
| 🎡 **Рулетка** | Ставь на число (x35), цвет (x1) или диапазон (x2). |

### 💰 Финансы
- **Пополнение** — выбор суммы с реквизитами для перевода (USDT TRC20 / другие).
- **Вывод** — заявка от 1000 ₽ с указанием реквизитов. Уведомление админам в Telegram.

### 🎁 Бонусы
- **Ежедневная рулетка** — крути раз в 24 часа и получай от +10% до удвоения баланса.

### 🛡️ Админ-панель
| Команда | Описание |
|---------|----------|
| 📢 Рассылка | HTML-рассылка всем пользователям |
| ➕ Добавить баланс | Пополнение баланса любому юзеру по ID |
| 🚫 Заблокировать / ✅ Разблокировать | Блокировка с уведомлением игрока |
| 📊 Статистика | Количество юзеров, пополнения, покупки, общий баланс |
| 🔧 Подкрутка | Изменение множителя для любой игры |

### 🔒 Безопасность
- Проверка блокировки на **все** события (сообщения + inline-кнопки).
- Автоматическое создание пользователя при первом `/start`.
- Списание ставки **до** начала игры — нет «висячих» ставок.

---

## 🚀 Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/palimps3st/telegram-casino-bot.git
cd telegram-casino-bot
```

### 2. Установка зависимостей
Рекомендуется использовать виртуальное окружение (`venv`):
```bash
python -m venv venv
source venv/bin/activate  # Для Linux/Mac
# venv\Scripts\activate   # Для Windows

pip install aiogram sqlalchemy aiosqlite bcrypt
```

### 3. Настройка
Открой файл `settings.py` и заполни базовые переменные:
```python
BOT_TOKEN = "123456:ABC-DEF..."          # Токен от @BotFather
ADMINS = [123456789]                     # Telegram ID администраторов
TECH_SUPPORT_USER_ID = 123456789         # ID техподдержки (куда летят обращения)
```

### 4. Запуск бота
```bash
python main.py
```

---

## 📁 Структура проекта

```text
tg-bot/
├── main.py                     # Точка входа
├── settings.py                 # Конфигурация
├── db/
│   ├── database.py             # Подключение к SQLite
│   └── models.py               # SQLAlchemy модели
├── bot/
│   ├── keyboards.py            # Reply/Inline клавиатуры
│   ├── middlewares/
│   │   └── block_check.py      # Проверка блокировки
│   └── handlers/
│       ├── auth.py             # Авторегистрация
│       ├── profile.py          # Профиль пользователя
│       ├── common.py           # Кнопка «Назад»
│       ├── top_up.py           # Пополнение и вывод
│       ├── support.py          # Техподдержка
│       ├── bonuses.py          # Бонусная рулетка
│       ├── admin_handlers.py   # Админ-панель
│       └── games/
│           ├── games_menu.py   # Меню игр
│           ├── slots.py
│           ├── roulette.py
│           ├── blackjack.py
│           ├── mines.py
│           ├── crash.py
│           └── even_odd.py
└── README.md
```

---

## 🛠 Технологии

- **Python 3.10+**
- **aiogram 3.x** — асинхронный фреймворк для Telegram Bot API
- **SQLAlchemy 2.0 + aiosqlite** — асинхронная ORM и база данных SQLite 
- **aiogram FSM** — машина состояний для пошаговых процессов и игр

## 📄 Лицензия

Проект распространяется под лицензией **MIT**. 
