from aiogram import Router, F
from aiogram.types import Message
from db.database import AsyncSessionLocal
from db.models import User
from sqlalchemy import select
from bot.keyboards import main_menu, back_button

router = Router()

@router.message(F.text == "Профиль")
async def show_profile(message: Message):
    user_id = message.from_user.id
    async with AsyncSessionLocal() as session:
        user = await session.execute(select(User).where(User.tg_id == user_id))
        user = user.scalar()

        if not user:
            await message.answer("❌ Ошибка: пользователь не найден.", reply_markup=back_button())
            return

        text = (
            f"📝 Профиль:\n"
            f"👤 ID: <code>{user.tg_id}</code>\n"
            f"💰 Баланс: {user.balance:.2f} ₽\n\n"
            f'🔗 <a href="https://t.me/autobattIe">Наш канал</a>\n'
            f'💬 <a href="https://t.me/+ZGP8OUDA3iJmOTMy">Наш чат</a>'
        )

        await message.answer(text, parse_mode="HTML", reply_markup=back_button())