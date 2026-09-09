
from aiogram import Router, F
from aiogram.types import Message
from bot.keyboards import main_menu, admin_menu, games_menu
router = Router()

@router.message(F.text == "🔙 Назад")
async def back_to_main(message: Message):
    await message.answer(
        "Главное меню:",
        reply_markup=main_menu(user_id=message.from_user.id)  # Динамическое меню
    )