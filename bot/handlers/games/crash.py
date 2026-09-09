import asyncio
import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from db.database import AsyncSessionLocal
from db.models import User
from sqlalchemy import select
from bot.keyboards import games_menu, bet_kb

router = Router()

class CrashStates(StatesGroup):
    BET = State()
    COEFF_INPUT = State()
    FLYING = State()

CRASH_PROBABILITY = 0.025
MULTIPLIER_STEP = 0.01
BASE_MULTIPLIER = 1.00
UPDATE_INTERVAL = 0.1

async def rocket_animation(message: Message, state: FSMContext, stop_event: asyncio.Event):
    data = await state.get_data()
    current_multiplier = data['multiplier']
    bet = data['bet']
    target_coeff = data.get('target_coeff')

    frames = [
        "🚀✨▰▰▰▰▰▰▰▰▰",
        "▰🚀✨▰▰▰▰▰▰▰▰",
        "▰▰🚀✨▰▰▰▰▰▰▰",
        "▰▰▰🚀✨▰▰▰▰▰▰",
        "▰▰▰▰🚀✨▰▰▰▰▰",
        "▰▰▰▰▰🚀✨▰▰▰▰",
        "▰▰▰▰▰▰🚀✨▰▰▰",
        "▰▰▰▰▰▰▰🚀✨▰▰",
        "▰▰▰▰▰▰▰▰🚀✨▰",
        "▰▰▰▰▰▰▰▰▰🚀✨"
    ]

    msg = await message.answer("Запуск...")
    try:
        while not stop_event.is_set():
            current_multiplier += MULTIPLIER_STEP
            await state.update_data(multiplier=current_multiplier)

            if target_coeff and current_multiplier >= target_coeff:
                stop_event.set()
                win = bet * current_multiplier
                async with AsyncSessionLocal() as session:
                    user = (await session.execute(select(User).where(User.tg_id == message.from_user.id))).scalar()
                    user.balance += win
                    await session.commit()
                await msg.edit_text(
                    f"🎉 Цель достигнута x{current_multiplier:.2f}!\n"
                    f"💰 Выигрыш: {win:.2f} ₽\n"
                    f"💵 Баланс: {user.balance:.2f} ₽"
                )
                await message.answer("Выберите игру:", reply_markup=games_menu())
                await state.clear()
                return

            frame = frames[int(current_multiplier * 10) % len(frames)]
            text = (
                f"{frame}\n"
                f"📈 Множитель: x{current_multiplier:.2f}\n"
                f"💰 Потенциал: {bet * current_multiplier:.2f} ₽"
            )
            await msg.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=f"🛑 Забрать x{current_multiplier:.2f}", callback_data="cashout")]
                ])
            )

            if random.random() < CRASH_PROBABILITY:
                await msg.edit_text(f"💥 Краш на x{current_multiplier:.2f}!")
                await message.answer("🍀 Повезёт в следующий раз!", reply_markup=games_menu())
                await state.clear()
                return

            await asyncio.sleep(UPDATE_INTERVAL)
    except asyncio.CancelledError:
        pass

@router.message(F.text == "🚀Ракета🚀")
async def start_crash(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("💰 Введите ставку:", reply_markup=bet_kb())
    await state.set_state(CrashStates.BET)

@router.message(CrashStates.BET, F.text == "🔙 Назад")
async def cancel_bet(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Отменено", reply_markup=games_menu())

@router.message(CrashStates.BET)
async def process_bet(message: Message, state: FSMContext):
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
        user = (await session.execute(select(User).where(User.tg_id == message.from_user.id))).scalar()
        if not user or user.balance < bet:
            await state.clear()
            return await message.answer("❌ Недостаточно средств!", reply_markup=games_menu())
        user.balance -= bet
        await session.commit()

    await state.update_data(bet=bet)
    await state.set_state(CrashStates.COEFF_INPUT)
    await message.answer(
        "Введите целевой множитель (например 1.5, 2.0) или '🔙 Назад':",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Примеры: 1.5 | 2.0 | 3.0", callback_data="example")
        ]])
    )

@router.message(CrashStates.COEFF_INPUT, F.text == "🔙 Назад")
async def cancel_coeff(message: Message, state: FSMContext):
    # Ставка уже сгорела, возврата нет
    await state.clear()
    await message.answer("❌ Игра отменена", reply_markup=games_menu())

@router.message(CrashStates.COEFF_INPUT)
async def process_coeff(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        return await cancel_coeff(message, state)
    try:
        target = float(message.text.strip())
        if target <= 1.0:
            raise ValueError
    except ValueError:
        await state.clear()
        return await message.answer("❌ Коэффициент > 1.0!", reply_markup=games_menu())

    await state.update_data(target_coeff=target, multiplier=BASE_MULTIPLIER)
    await state.set_state(CrashStates.FLYING)
    stop_event = asyncio.Event()
    await state.update_data(stop_event=stop_event)
    await rocket_animation(message, state, stop_event)

@router.callback_query(CrashStates.FLYING, F.data == "cashout")
async def cashout_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data['stop_event'].set()
    mult = data['multiplier']
    bet = data['bet']
    win = bet * mult

    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.tg_id == callback.from_user.id))).scalar()
        user.balance += win
        await session.commit()

    await callback.message.edit_text(
        f"🎉 Кэшаут!\n🏆 x{mult:.2f}\n💰 +{win:.2f} ₽\n💵 Баланс: {user.balance:.2f} ₽"
    )
    await callback.message.answer("Выберите игру:", reply_markup=games_menu())
    await state.clear()