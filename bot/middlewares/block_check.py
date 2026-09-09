from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from db.database import AsyncSessionLocal
from db.models import User
from sqlalchemy import select

class BlockCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        if user_id:
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(User).where(User.tg_id == user_id))
                user = result.scalar()
                if user and user.is_blocked:
                    if isinstance(event, CallbackQuery):
                        await event.answer("🚫 Вы заблокированы!", show_alert=True)
                    else:
                        await event.answer("🚫 Вы заблокированы!")
                    return
        return await handler(event, data)