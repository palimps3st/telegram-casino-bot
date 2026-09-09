from aiogram import Router, F
from aiogram.types import Message
from bot.keyboards import purchase_menu, back_button
from db.database import AsyncSessionLocal
from db.models import User
from datetime import datetime, timedelta
from sqlalchemy import select
import random
from bot.keyboards import main_menu, admin_menu, games_menu
router = Router()


@router.message(F.text == "Покупка")
async def show_purchase_menu(message: Message):
    await message.answer("Выберите тариф подписки:", reply_markup=purchase_menu())


@router.message(F.text.in_(
    ["1 месяц (350 ₽)", "3 месяца (950 ₽)",
     "6 месяцев (1700 ₽)", "1 год (3200 ₽)"]
))
async def process_purchase(message: Message):
    user_id = message.from_user.id
    async with AsyncSessionLocal() as session:
        user = await session.execute(
            select(User).where(User.tg_id == user_id)
        )
        user = user.scalar()

        if not user:
            await message.answer("Вы не зарегистированы!", reply_markup=back_button())
            return

        # Используем словарь для явного указания месяца и цены
        tariff_map = {
            "1 месяц (350 ₽)": (350, 1),
            "3 месяца (950 ₽)": (950, 3),
            "6 месяцев (1700 ₽)": (1700, 6),
            "1 год (3200 ₽)": (3200, 12)
        }

        # Получаем цену и срок из словаря
        tariff = tariff_map.get(message.text)
        if not tariff:
            await message.answer("Тариф не найден.")
            return

        price, months = tariff

        if user.balance < price:
            await message.answer(f"Недостаточно средств! Нужно: {price} ₽")
            return

        # Обновляем баланс и подписку
        user.balance -= price
        current_end = user.subscription_end if user.subscription_end else datetime.now()
        user.subscription_end = current_end + timedelta(days=months * 30)

        await session.commit()

        await message.answer(
            f"Подписка продлена на {months} месяцев! Текущий баланс: {user.balance} ₽",
            reply_markup=back_button()
        )