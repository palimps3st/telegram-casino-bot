import asyncio
import random
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from db.database import AsyncSessionLocal
from db.models import User
from sqlalchemy import select
from bot.keyboards import (
    roulette_bet_types_kb, roulette_colors_kb,
    roulette_ranges_kb, roulette_numbers_kb, games_menu, bet_kb
)

router = Router()

class RouletteStates(StatesGroup):
    CHOOSE_BET_TYPE = State()
    CHOOSE_NUMBER = State()
    CHOOSE_COLOR = State()
    CHOOSE_RANGE = State()
    CONFIRM_BET = State()

ROULETTE_NUMBERS = list(range(0, 37))
COLOR_MAP = {
    "🔴 Красный": [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36],
    "⚫ Черный": [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35],
    "🟢 Зеленый": [0]
}
RANGE_MAP = {
    "1️⃣-1️⃣2️⃣": (1, 12),
    "1️⃣3️⃣-2️⃣4️⃣": (13, 24),
    "2️⃣5️⃣-3️⃣6️⃣": (25, 36)
}

async def spin_animation(message: Message, result: int):
    msg = await message.answer("🌀 Крутим...")
    previous = None
    for _ in range(10):
        while True:
            num = random.randint(0, 36)
            val = f"{get_color_emoji(num)} {num}"
            if val != previous:
                break
        try:
            await msg.edit_text(val)
        except Exception:
            pass
        await asyncio.sleep(0.15)
        previous = val
    
    await msg.edit_text(f"🎯 {get_color_emoji(result)} {result} | {get_color_name(result)}")

def get_color_emoji(n: int) -> str:
    if n == 0: return "🟢"
    return "🔴" if n in COLOR_MAP["🔴 Красный"] else "⚫"

def get_color_name(n: int) -> str:
    if n == 0: return "Зеленый"
    return "Красный" if n in COLOR_MAP["🔴 Красный"] else "Черный"

@router.message(F.text == "🎰Рулетка🎰")
async def start_roulette(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🎰 Выберите тип ставки:", reply_markup=roulette_bet_types_kb())
    await state.set_state(RouletteStates.CHOOSE_BET_TYPE)

@router.message(RouletteStates.CHOOSE_BET_TYPE, F.text == "🔙 Назад")
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Отменено", reply_markup=games_menu())

@router.message(RouletteStates.CHOOSE_BET_TYPE)
async def process_bet_type(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        return await cancel(message, state)
    if "Число" in message.text:
        await message.answer("🔢 Выберите число:", reply_markup=roulette_numbers_kb())
        await state.set_state(RouletteStates.CHOOSE_NUMBER)
    elif "Цвет" in message.text:
        await message.answer("🎨 Выберите цвет:", reply_markup=roulette_colors_kb())
        await state.set_state(RouletteStates.CHOOSE_COLOR)
    elif "Диапазон" in message.text:
        await message.answer("📊 Выберите диапазон:", reply_markup=roulette_ranges_kb())
        await state.set_state(RouletteStates.CHOOSE_RANGE)
    else:
        await message.answer("❌ Выберите из меню!")

@router.message(RouletteStates.CHOOSE_NUMBER, F.text == "🔙 Назад")
async def cancel_n(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Отменено", reply_markup=games_menu())

@router.message(RouletteStates.CHOOSE_NUMBER)
async def process_number(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        return await cancel_n(message, state)
    try:
        n = int(message.text.strip())
        if not (0 <= n <= 36):
            raise ValueError
        await state.update_data(bet_type="number", bet_value=n)
        await ask_bet(message, state)
    except ValueError:
        await state.clear()
        await message.answer("❌ Неверное число!", reply_markup=games_menu())

@router.message(RouletteStates.CHOOSE_COLOR, F.text == "🔙 Назад")
async def cancel_c(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Отменено", reply_markup=games_menu())

@router.message(RouletteStates.CHOOSE_COLOR)
async def process_color(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        return await cancel_c(message, state)
    if message.text not in COLOR_MAP:
        await state.clear()
        return await message.answer("❌ Неверный цвет!", reply_markup=games_menu())
    await state.update_data(bet_type="color", bet_value=message.text)
    await ask_bet(message, state)

@router.message(RouletteStates.CHOOSE_RANGE, F.text == "🔙 Назад")
async def cancel_r(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Отменено", reply_markup=games_menu())

@router.message(RouletteStates.CHOOSE_RANGE)
async def process_range(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        return await cancel_r(message, state)
    if message.text not in RANGE_MAP:
        await state.clear()
        return await message.answer("❌ Неверный диапазон!", reply_markup=games_menu())
    await state.update_data(bet_type="range", bet_value=message.text)
    await ask_bet(message, state)

async def ask_bet(message: Message, state: FSMContext):
    await message.answer("💰 Введите сумму ставки:", reply_markup=bet_kb())
    await state.set_state(RouletteStates.CONFIRM_BET)

@router.message(RouletteStates.CONFIRM_BET, F.text == "🔙 Назад")
async def cancel_bet(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Отменено", reply_markup=games_menu())

@router.message(RouletteStates.CONFIRM_BET)
async def process_bet_amount(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        return await cancel_bet(message, state)
    try:
        bet = float(message.text.replace("₽", "").strip())
        if bet <= 0:
            raise ValueError
    except ValueError:
        await state.clear()
        return await message.answer("❌ Некорректная сумма!", reply_markup=games_menu())

    async with AsyncSessionLocal() as session:
        user = await session.execute(select(User).where(User.tg_id == message.from_user.id))
        user = user.scalar()
        if not user or user.balance < bet:
            await state.clear()
            return await message.answer("❌ Недостаточно средств!", reply_markup=games_menu())

        # СПИСЫВАЕМ СТАВКУ
        user.balance -= bet
        await session.commit()

        result = random.choice(ROULETTE_NUMBERS)
        await spin_animation(message, result)

        data = await state.get_data()
        win = check_win(data, result)
        mult = get_multiplier(data["bet_type"])
        
        if win:
            payout = bet * (mult + 1)  # Возврат + выигрыш
            user.balance += payout
            text = f"🎉 Выигрыш: +{bet * mult:.2f} ₽"
        else:
            text = f"😞 Проигрыш: -{bet:.2f} ₽"
        
        await session.commit()
        await message.answer(f"{text}\n💰 Баланс: {user.balance:.2f} ₽", reply_markup=games_menu())
        await state.clear()

def check_win(data: dict, result: int) -> bool:
    bt, val = data["bet_type"], data["bet_value"]
    if bt == "number":
        return int(val) == result
    elif bt == "color":
        return result in COLOR_MAP[val]
    elif bt == "range":
        s, e = RANGE_MAP[val]
        return s <= result <= e

def get_multiplier(bt: str) -> float:
    return {"number": 35, "color": 1, "range": 2}[bt]