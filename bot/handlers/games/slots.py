import random
import asyncio
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from db.database import AsyncSessionLocal
from db.models import User
from sqlalchemy import select
from bot.keyboards import games_menu, bet_kb

router = Router()

SLOT_SYMBOLS = {
    "🍒": {"base": 1, "triple": 3},
    "🍊": {"base": 2, "triple": 5},
    "🍋": {"base": 3, "triple": 8},
    "💎": {"base": 5, "triple": 15},
    "7️⃣": {"base": 10, "triple": 30},
    "🔔": {"base": 7, "triple": 20}
}

class SlotsStates(StatesGroup):
    BET = State()

async def spin_animation(message: Message, final_result: list):
    frames = ["🎰|🌀|🌀", "🌀|🎰|🌀", "🌀|🌀|🎰", "|".join(final_result)]
    msg = await message.answer("Крутим...")
    for frame in frames:
        await asyncio.sleep(0.5)
        try:
            await msg.edit_text(frame)
        except Exception:
            pass

@router.message(F.text == "💎Слоты💎")
async def start_slots(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("💰 Введите ставку:", reply_markup=bet_kb())
    await state.set_state(SlotsStates.BET)

@router.message(SlotsStates.BET, F.text == "🔙 Назад")
async def cancel_bet(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Отменено", reply_markup=games_menu())

@router.message(SlotsStates.BET)
async def process_slots(message: Message, state: FSMContext):
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
        if not user:
            await state.clear()
            return await message.answer("❌ Ошибка!", reply_markup=games_menu())
        if user.balance < bet:
            await state.clear()
            return await message.answer("❌ Недостаточно средств!", reply_markup=games_menu())

        user.balance -= bet
        symbols = list(SLOT_SYMBOLS.keys())
        result = [random.choice(symbols) for _ in range(3)]
        await spin_animation(message, result)

        # Исправленная логика
        if result[0] == result[1] == result[2]:
            mult = SLOT_SYMBOLS[result[0]]["triple"]
        elif result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:
            # Находим пару
            pair_sym = result[0] if result[0] == result[1] else result[2]
            mult = SLOT_SYMBOLS[pair_sym]["base"]
        else:
            mult = 0

        win = bet * mult
        user.balance += win
        await session.commit()

        await message.answer(
            f"🎰 {' '.join(result)}\n"
            f"Множитель: x{mult}\n"
            f"💵 Выигрыш: {win:.2f} ₽\n"
            f"💰 Баланс: {user.balance:.2f} ₽",
            reply_markup=games_menu()
        )
        await state.clear()