from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from db.models import User
from db.database import AsyncSessionLocal
from aiogram.filters import Command
from sqlalchemy import select
from settings import ADMINS
from bot.keyboards import main_menu

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.tg_id == user_id))
        user = result.scalar()
        
        if not user:
            user = User(
                tg_id=user_id,
                login=f"user_{user_id}",
                balance=0.0,
                is_blocked=False
            )
            session.add(user)
            await session.commit()
            
        await message.answer(
            "👋 Добро пожаловать в казино!\n\n"
            "🎮 Игры — выбор игр\n"
            "💰 Пополнить — пополнить баланс\n"
            "💸 Вывод — вывести средства\n"
            "🎁 Бонусы — ежедневная рулетка\n"
            "🆘 Тех. поддержка — связь с админами",
            reply_markup=main_menu(user_id)
        )