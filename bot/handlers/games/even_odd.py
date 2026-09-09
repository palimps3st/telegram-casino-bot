import random
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from db.database import AsyncSessionLocal
from db.models import User
from sqlalchemy import select
from bot.keyboards import games_menu, even_odd_kb, bet_kb

router = Router()

class EvenOddStates(StatesGroup):
    BET = State()
    CHOICE = State()

@router.message(F.text == "🎲Чет/Нечет🎲")
async def game_even_odd(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("💰 Сделайте ставку:", reply_markup=bet_kb())
    await state.set_state(EvenOddStates.BET)

@router.message(EvenOddStates.BET)
async def process_bet(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=games_menu())
        return
    try:
        bet = float(message.text.replace("₽", "").strip())
        if bet <= 0:
            raise ValueError
    except ValueError:
        await state.clear()
        await message.answer("❌ Некорректная сумма!", reply_markup=games_menu())
        return

    async with AsyncSessionLocal() as session:
        user = await session.execute(select(User).where(User.tg_id == message.from_user.id))
        user = user.scalar()
        if not user:
            await message.answer("❌ Ошибка!", reply_markup=games_menu())
            await state.clear()
            return
        if user.balance < bet:
            await message.answer(f"❌ Недостаточно средств! Баланс: {user.balance:.2f} ₽", reply_markup=games_menu())
            await state.clear()
            return

        # СПИСЫВАЕМ СТАВКУ
        user.balance -= bet
        await session.commit()
        await state.update_data(bet=bet)
        await message.answer("Выберите:", reply_markup=even_odd_kb())
        await state.set_state(EvenOddStates.CHOICE)

@router.message(EvenOddStates.CHOICE, F.text == "🔙 Назад")
async def cancel_choice(message: Message, state: FSMContext):
    # Ставка уже списана, возврат не делаем (игра началась)
    await state.clear()
    await message.answer("❌ Игра отменена", reply_markup=games_menu())

@router.message(EvenOddStates.CHOICE, F.text.in_(["Чет", "Нечет"]))
async def process_choice(message: Message, state: FSMContext):
    data = await state.get_data()
    bet = data.get("bet")
    
    async with AsyncSessionLocal() as session:
        user = await session.execute(select(User).where(User.tg_id == message.from_user.id))
        user = user.scalar()
        
        number = random.randint(1, 100)
        is_even = number % 2 == 0
        choice = message.text.lower()
        win = (choice == "чет" and is_even) or (choice == "нечет" and not is_even)

        if win:
            user.balance += bet * 2  # Возврат ставки + выигрыш 1:1
            result = f"✅ Выигрыш! Число: {number}"
        else:
            result = f"❌ Проигрыш! Число: {number}"
        
        await session.commit()
        await message.answer(
            f"{result}\n💰 Баланс: {user.balance:.2f} ₽",
            reply_markup=games_menu()
        )
        await state.clear()