from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from settings import ADMINS

def main_menu(user_id: int = None):
    buttons = [
        ["Профиль", "Игры"],
        ["Пополнить", "Вывод"],
        ["Бонусы", "Тех. поддержка"]
    ]
    if user_id and user_id in ADMINS:
        buttons.append(["Админ панель"])
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=text) for text in row] for row in buttons],
        resize_keyboard=True
    )

def admin_menu():
    buttons = [
        ["Рассылка", "Добавить баланс"],
        ["Заблокировать", "Разблокировать"],
        ["Статистика", "Подкрутка"],
        ["Выйти из админки"]
    ]
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=text) for text in row] for row in buttons],
        resize_keyboard=True
    )

def mines_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="3"), KeyboardButton(text="5"), KeyboardButton(text="7")],
            [KeyboardButton(text="9"), KeyboardButton(text="10"), KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )

def games_menu():
    buttons = [
        ["🎲Чет/Нечет🎲", "💎Слоты💎"],
        ["🎰Рулетка🎰", "🃏Blackjack🃏", "💣Мины💣"],
        ["🚀Ракета🚀"],
        ["🔙 Назад"]
    ]
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=text) for text in row] for row in buttons],
        resize_keyboard=True
    )

def roulette_bet_types_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔢 Число"), KeyboardButton(text="🎨 Цвет")],
            [KeyboardButton(text="📊 Диапазон"), KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )

def roulette_colors_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔴 Красный"), KeyboardButton(text="⚫ Черный")],
            [KeyboardButton(text="🟢 Зеленый"), KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )

def roulette_ranges_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="1️⃣-1️⃣2️⃣"), KeyboardButton(text="1️⃣3️⃣-2️⃣4️⃣")],
            [KeyboardButton(text="2️⃣5️⃣-3️⃣6️⃣"), KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )

def roulette_numbers_kb():
    buttons = [
        [KeyboardButton(text=str(i)) for i in range(0, 13)],
        [KeyboardButton(text=str(i)) for i in range(13, 25)],
        [KeyboardButton(text=str(i)) for i in range(25, 37)],
        [KeyboardButton(text="🔙 Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def even_odd_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Чет"), KeyboardButton(text="Нечет")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )

def bet_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="50 ₽"), KeyboardButton(text="100 ₽"), KeyboardButton(text="200 ₽")],
            [KeyboardButton(text="500 ₽"), KeyboardButton(text="1000 ₽")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )

def bonuses_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Рулетка")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )

def top_up_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="500 ₽"), KeyboardButton(text="1000 ₽")],
            [KeyboardButton(text="2000 ₽"), KeyboardButton(text="5000 ₽")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )

def back_button():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True
    )

def profile_menu():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True
    )