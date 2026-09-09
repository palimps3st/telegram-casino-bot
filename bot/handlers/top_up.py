from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from bot.keyboards import top_up_menu, back_button, main_menu
from db.database import AsyncSessionLocal
from db.models import User
from sqlalchemy import select

router = Router()

class WithdrawStates(StatesGroup):
    AMOUNT = State()
    DETAILS = State()

@router.message(F.text == "Пополнить")
async def show_top_up_menu(message: Message):
    await message.answer("Выберите сумму пополнения:", reply_markup=top_up_menu())

@router.message(F.text.in_(["500 ₽", "1000 ₽", "2000 ₽", "5000 ₽"]))
async def process_top_up(message: Message):
    amount = int(message.text.split(" ")[0])
    await message.answer(
        f"💳 Пополнение: {amount} ₽\n\n"
        f"Реквизиты для перевода:\n"
        f"`TCgDk...XyZ9` (USDT TRC20)\n\n"
        f"После оплаты отправьте скриншот в тех. поддержку.",
        parse_mode="Markdown",
        reply_markup=back_button()
    )

# --- Вывод ---
@router.message(F.text == "Вывод")
async def start_withdraw(message: Message, state: FSMContext):
    await message.answer(
        "💸 Введите сумму вывода (мин. 1000 ₽):",
        reply_markup=back_button()
    )
    await state.set_state(WithdrawStates.AMOUNT)

@router.message(WithdrawStates.AMOUNT)
async def process_withdraw_amount(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.clear()
        await message.answer("Отменено", reply_markup=main_menu(user_id=message.from_user.id))
        return
    try:
        amount = float(message.text.replace("₽", "").strip())
        if amount < 1000:
            await message.answer("❌ Минимум 1000 ₽!")
            return
        
        async with AsyncSessionLocal() as session:
            user = await session.execute(select(User).where(User.tg_id == message.from_user.id))
            user = user.scalar()
            if not user or user.balance < amount:
                await message.answer("❌ Недостаточно средств!")
                await state.clear()
                return
        
        await state.update_data(amount=amount)
        await message.answer("Введите реквизиты (кошелек USDT или карта):")
        await state.set_state(WithdrawStates.DETAILS)
    except ValueError:
        await message.answer("❌ Введите число!")

@router.message(WithdrawStates.DETAILS)
async def process_withdraw_details(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.clear()
        await message.answer("Отменено", reply_markup=main_menu(user_id=message.from_user.id))
        return
    
    data = await state.get_data()
    amount = data["amount"]
    details = message.text
    
    # Здесь отправка админу
    from settings import ADMINS
    for admin_id in ADMINS:
        try:
            await message.bot.send_message(
                admin_id,
                f"💸 Новая заявка на вывод!\n"
                f"👤 ID: {message.from_user.id}\n"
                f"💰 Сумма: {amount:.2f} ₽\n"
                f"📋 Реквизиты: {details}"
            )
        except Exception:
            pass
    
    await message.answer(
        "✅ Заявка на вывод отправлена!\n"
        "Ожидайте обработки администратором.",
        reply_markup=main_menu(user_id=message.from_user.id)
    )
    await state.clear()