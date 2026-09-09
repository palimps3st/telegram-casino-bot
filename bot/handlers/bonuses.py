from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
import random
from db.database import AsyncSessionLocal
from db.models import User, Coupon
from bot.keyboards import bonuses_menu, back_button, main_menu
from sqlalchemy import select

router = Router()

ROULETTE_OPTIONS = [
    {"text": "+10% к балансу", "chance": 0.45, "multiplier": 0.10},
    {"text": "+25% к балансу", "chance": 0.30, "multiplier": 0.25},
    {"text": "+50% к балансу", "chance": 0.15, "multiplier": 0.50},
    {"text": "Удвоение баланса", "chance": 0.10, "multiplier": 1.00}
]

class BonusStates(StatesGroup):
    ACTIVATE_COUPON = State()

@router.message(F.text == "Бонусы")
async def show_bonuses(message: Message):
    await message.answer("🎁 Бонусы:", reply_markup=bonuses_menu())

@router.message(F.text == "Рулетка")
async def spin_roulette(message: Message):
    user_id = message.from_user.id
    async with AsyncSessionLocal() as session:
        user = await session.execute(select(User).where(User.tg_id == user_id))
        user = user.scalar()

        if not user:
            return

        # Кулдаун: раз в сутки
        if user.last_roulette_spin and (datetime.now() - user.last_roulette_spin) < timedelta(hours=24):
            remaining = timedelta(hours=24) - (datetime.now() - user.last_roulette_spin)
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            await message.answer(f"⏳ Рулетка доступна через {hours}ч {minutes}м!")
            return

        weights = [opt["chance"] for opt in ROULETTE_OPTIONS]
        result = random.choices(ROULETTE_OPTIONS, weights=weights, k=1)[0]
        
        win_amount = user.balance * result["multiplier"]
        user.balance += win_amount
        user.last_roulette_spin = datetime.now()
        await session.commit()

        await message.answer(
            f"🎉 {result['text']}!\n"
            f"💵 Начислено: +{win_amount:.2f} ₽\n"
            f"💰 Баланс: {user.balance:.2f} ₽",
            reply_markup=back_button()
        )