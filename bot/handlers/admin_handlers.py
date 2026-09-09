from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, update
from db.database import AsyncSessionLocal
from bot.keyboards import main_menu, admin_menu, back_button
from settings import ADMINS
from db.models import User, GameSettings, Transaction

router = Router()

class AdminStates(StatesGroup):
    BROADCAST_MESSAGE = State()
    ADD_BALANCE_USER_ID = State()
    ADD_BALANCE_AMOUNT = State()
    BLOCK_USER = State()
    UNBLOCK_USER = State()
    GAME_MULTIPLIER_NAME = State()
    GAME_MULTIPLIER_VALUE = State()

async def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

@router.message(F.text == "Админ панель", F.from_user.id.in_(ADMINS))
async def show_admin_panel(message: Message):
    await message.answer("Админ-панель:", reply_markup=admin_menu())

@router.message(F.text == "Выйти из админки")
async def exit_admin(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu(user_id=message.from_user.id))

# --- Рассылка ---
@router.message(F.text == "Рассылка")
async def start_broadcast(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    await message.answer(
        "👇 Введите текст для рассылки (HTML разрешён):",
        reply_markup=back_button()
    )
    await state.set_state(AdminStates.BROADCAST_MESSAGE)

@router.message(AdminStates.BROADCAST_MESSAGE)
async def process_broadcast(message: Message, state: FSMContext, bot):
    if message.text == "🔙 Назад":
        await state.clear()
        await message.answer("Отменено", reply_markup=admin_menu())
        return

    async with AsyncSessionLocal() as session:
        users = await session.execute(select(User))
        count = 0
        for user in users.scalars():
            try:
                await bot.send_message(
                    chat_id=user.tg_id,
                    text=message.text,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
                count += 1
            except Exception:
                pass
    await message.answer(f"✅ Рассылка завершена! Доставлено: {count}", reply_markup=admin_menu())
    await state.clear()

# --- Разблокировать ---
@router.message(F.text == "Разблокировать")
async def unblock_user_start(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    await message.answer("Введите ID пользователя:", reply_markup=back_button())
    await state.set_state(AdminStates.UNBLOCK_USER)

@router.message(AdminStates.UNBLOCK_USER)
async def process_unblock_user(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.clear()
        await message.answer("Отменено", reply_markup=admin_menu())
        return
    try:
        target_id = int(message.text)
        async with AsyncSessionLocal() as session:
            await session.execute(update(User).where(User.tg_id == target_id).values(is_blocked=False))
            await session.commit()
            try:
                await message.bot.send_message(target_id, "✅ Ваша блокировка снята!")
            except Exception:
                pass
        await message.answer(f"✅ Пользователь {target_id} разблокирован!", reply_markup=admin_menu())
    except ValueError:
        await message.answer("❌ Введите число!")
    finally:
        await state.clear()

# --- Добавить баланс ---
@router.message(F.text == "Добавить баланс")
async def add_balance_start(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    await message.answer("Введите ID пользователя:", reply_markup=back_button())
    await state.set_state(AdminStates.ADD_BALANCE_USER_ID)

@router.message(AdminStates.ADD_BALANCE_USER_ID)
async def add_balance_user_id(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.clear()
        await message.answer("Отменено", reply_markup=admin_menu())
        return
    try:
        await state.update_data(user_id=int(message.text))
        await message.answer("Введите сумму:")
        await state.set_state(AdminStates.ADD_BALANCE_AMOUNT)
    except ValueError:
        await message.answer("❌ Введите число!")

@router.message(AdminStates.ADD_BALANCE_AMOUNT)
async def add_balance_amount(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.clear()
        await message.answer("Отменено", reply_markup=admin_menu())
        return
    try:
        amount = float(message.text)
        if amount <= 0:
            await message.answer("❌ Сумма должна быть > 0!")
            return
        data = await state.get_data()
        async with AsyncSessionLocal() as session:
            user = await session.execute(select(User).where(User.tg_id == data["user_id"]))
            user = user.scalar()
            if not user:
                await message.answer("❌ Пользователь не найден!", reply_markup=admin_menu())
                await state.clear()
                return
            user.balance += amount
            await session.commit()
        await message.answer(f"✅ Баланс обновлён! Новый баланс: {user.balance:.2f} ₽", reply_markup=admin_menu())
    except ValueError:
        await message.answer("❌ Введите число!")
    finally:
        await state.clear()

# --- Блокировка ---
@router.message(F.text == "Заблокировать")
async def block_user_start(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    await message.answer("Введите ID пользователя:", reply_markup=back_button())
    await state.set_state(AdminStates.BLOCK_USER)

@router.message(AdminStates.BLOCK_USER)
async def block_user_process(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.clear()
        await message.answer("Отменено", reply_markup=admin_menu())
        return
    try:
        target_id = int(message.text)
        async with AsyncSessionLocal() as session:
            await session.execute(update(User).where(User.tg_id == target_id).values(is_blocked=True))
            await session.commit()
            try:
                await message.bot.send_message(target_id, "🚫 Вы заблокированы администратором!")
            except Exception:
                pass
        await message.answer(f"✅ Пользователь {target_id} заблокирован!", reply_markup=admin_menu())
    except ValueError:
        await message.answer("❌ Введите число!")
    finally:
        await state.clear()

# --- Статистика ---
@router.message(F.text == "Статистика")
async def show_stats(message: Message):
    if not await is_admin(message.from_user.id):
        return
    async with AsyncSessionLocal() as session:
        users = await session.execute(select(User))
        users_all = users.scalars().all()
        topups = await session.execute(select(Transaction).where(Transaction.type == "topup"))
        purchases = await session.execute(select(Transaction).where(Transaction.type == "purchase"))
        topups = topups.scalars().all()
        purchases = purchases.scalars().all()
        
        stats_text = (
            f"👥 Пользователей: {len(users_all)}\n"
            f"💰 Пополнений: {len(topups)} на {sum(t.amount for t in topups):.2f} ₽\n"
            f"🛒 Покупок: {len(purchases)} на {sum(t.amount for t in purchases):.2f} ₽\n"
            f"📊 Общий баланс: {sum(u.balance for u in users_all):.2f} ₽"
        )
        await message.answer(stats_text, reply_markup=admin_menu())

# --- Подкрутка ---
@router.message(F.text == "Подкрутка")
async def adjust_multiplier_start(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    await message.answer("Введите название игры (slots / even_odd / roulette / blackjack / mines / crash):")
    await state.set_state(AdminStates.GAME_MULTIPLIER_NAME)

@router.message(AdminStates.GAME_MULTIPLIER_NAME)
async def adjust_multiplier_name(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.clear()
        await message.answer("Отменено", reply_markup=admin_menu())
        return
    valid_games = ["slots", "even_odd", "roulette", "blackjack", "mines", "crash"]
    game = message.text.lower().strip()
    if game not in valid_games:
        await message.answer(f"❌ Неверная игра. Доступны: {', '.join(valid_games)}")
        return
    await state.update_data(game_name=game)
    await message.answer("Введите множитель (например 1.0, 0.9, 1.2):")
    await state.set_state(AdminStates.GAME_MULTIPLIER_VALUE)

@router.message(AdminStates.GAME_MULTIPLIER_VALUE)
async def adjust_multiplier_value(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.clear()
        await message.answer("Отменено", reply_markup=admin_menu())
        return
    try:
        mult = float(message.text)
        data = await state.get_data()
        async with AsyncSessionLocal() as session:
            game = await session.execute(select(GameSettings).where(GameSettings.game_name == data["game_name"]))
            game = game.scalar()
            if not game:
                game = GameSettings(game_name=data["game_name"], multiplier=1.0)
                session.add(game)
            game.multiplier = mult
            await session.commit()
        await message.answer(f"✅ Множитель для {data['game_name']} = {mult}", reply_markup=admin_menu())
    except ValueError:
        await message.answer("❌ Введите число!")
    finally:
        await state.clear()