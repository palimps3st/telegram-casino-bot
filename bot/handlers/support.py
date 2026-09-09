# bot/handlers/support.py
from aiogram import Router, F
from aiogram.types import Message, ContentType
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from settings import TECH_SUPPORT_USER_ID
from bot.keyboards import back_button
from bot.keyboards import main_menu, admin_menu, games_menu
router = Router()


class SupportStates(StatesGroup):
    AWAITING_DESCRIPTION = State()


@router.message(F.text == "Тех. поддержка")
async def start_support_request(message: Message, state: FSMContext):
    await message.answer(
        "Опишите вашу проблему подробно. Вы можете прикрепить текст, фото или другие файлы. "
        "Мы ответим в ближайшее время.",
        reply_markup=back_button()
    )
    await state.set_state(SupportStates.AWAITING_DESCRIPTION)


@router.message(SupportStates.AWAITING_DESCRIPTION)
async def forward_to_support(message: Message, state: FSMContext, bot):
    # Формируем сообщение для техподдержки
    user_link = f"https://web.telegram.org/k/#{message.from_user.id}"
    user_info = f"👤 Пользователь: @{message.from_user.username or 'нет username'}\n🔗 Профиль: {user_link}"

    # Отправляем медиа-контент
    if message.content_type == ContentType.PHOTO:
        await bot.send_photo(
            chat_id=TECH_SUPPORT_USER_ID,
            photo=message.photo[-1].file_id,
            caption=f"{user_info}\n\n📨 Сообщение: {message.caption or 'Без текста'}"
        )
    elif message.content_type == ContentType.DOCUMENT:
        await bot.send_document(
            chat_id=TECH_SUPPORT_USER_ID,
            document=message.document.file_id,
            caption=f"{user_info}\n\n📨 Сообщение: {message.caption or 'Без текста'}"
        )
    else:
        await bot.send_message(
            chat_id=TECH_SUPPORT_USER_ID,
            text=f"{user_info}\n\n📨 Сообщение:\n{message.text}"
        )
    # Подтверждение пользователю
    await message.answer(
        "✅ Ваше обращение отправлено! Специалисты свяжутся с вами в ближайшее время.",
        reply_markup=back_button()
    )
    await state.clear()