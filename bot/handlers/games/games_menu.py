# bot/handlers/games/games_menu.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from bot.keyboards import games_menu

router = Router()

@router.message(F.text == "Игры")
async def show_games_menu(message: Message):
    """Обработчик кнопки 'Игры'"""
    await message.answer("🎮 Выберите игру:", reply_markup=games_menu())