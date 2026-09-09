import random
import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from db.database import AsyncSessionLocal
from db.models import User
from sqlalchemy import select
from bot.keyboards import games_menu, mines_keyboard, bet_kb

router = Router()

class MinesStates(StatesGroup):
    CHOOSE_BET = State()
    CHOOSE_MINES = State()
    PLAYING = State()

GRID_SIZE = 5
EMOJI_HIDDEN = "🟦"
EMOJI_MINE = "💣"
EMOJI_SAFE = "🟩"
BASE_MULTIPLIER = 1.25

async def generate_grid(mines: int):
    cells = [EMOJI_MINE] * mines + [EMOJI_SAFE] * (GRID_SIZE * GRID_SIZE - mines)
    random.shuffle(cells)
    grid = [cells[i*GRID_SIZE:(i+1)*GRID_SIZE] for i in range(GRID_SIZE)]
    return grid, [[False]*GRID_SIZE for _ in range(GRID_SIZE)]

@router.message(F.text == "💣Мины💣")
async def start_mines(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("💰 Введите сумму ставки:", reply_markup=bet_kb())
    await state.set_state(MinesStates.CHOOSE_BET)

@router.message(MinesStates.CHOOSE_BET, F.text == "🔙 Назад")
async def cancel_bet(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Отменено", reply_markup=games_menu())

@router.message(MinesStates.CHOOSE_BET)
async def process_bet(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        return await cancel_bet(message, state)
    try:
        bet = float(message.text.replace("₽", "").strip())
        if bet <= 0:
            raise ValueError
    except ValueError:
        await state.clear()
        return await message.answer("❌ Некорректная сумма!", reply_markup=games_menu())

    async with AsyncSessionLocal() as session:
        user = await session.execute(select(User).where(User.tg_id == message.from_user.id))
        user = user.scalar()
        if not user or user.balance < bet:
            await state.clear()
            return await message.answer("❌ Недостаточно средств!", reply_markup=games_menu())
        
        user.balance -= bet
        await session.commit()
        await state.update_data(bet=bet, balance=user.balance)
        await message.answer("💣 Выберите количество мин:", reply_markup=mines_keyboard())
        await state.set_state(MinesStates.CHOOSE_MINES)

@router.message(MinesStates.CHOOSE_MINES, F.text == "🔙 Назад")
async def cancel_mines(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Отменено", reply_markup=games_menu())

@router.message(MinesStates.CHOOSE_MINES)
async def process_mines_count(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        return await cancel_mines(message, state)
    try:
        mines = int(message.text)
        if not (3 <= mines <= 10):
            raise ValueError
    except ValueError:
        await state.clear()
        return await message.answer("❌ Неверное количество! (3-10)", reply_markup=games_menu())

    data = await state.get_data()
    grid, opened = await generate_grid(mines)
    await state.update_data(grid=grid, opened=opened, mines=mines, safe=0, multiplier=1.0, won=0.0)

    text = (
        f"💣 Мины: {mines}\n"
        f"💵 Ставка: {data['bet']:.2f} ₽\n"
        f"📈 Множитель: x1.00\n"
        f"💰 Возможный выигрыш: {data['bet']:.2f} ₽"
    )
    await message.answer(text, reply_markup=await render_grid(opened, True))
    await state.set_state(MinesStates.PLAYING)

async def render_grid(opened, show_controls=True):
    buttons = []
    for i, row in enumerate(opened):
        btn_row = []
        for j, cell in enumerate(row):
            text = "🟨" if cell else EMOJI_HIDDEN
            btn_row.append(InlineKeyboardButton(text=text, callback_data=f"{i}_{j}"))
        buttons.append(btn_row)
    if show_controls:
        buttons.append([InlineKeyboardButton(text="🏃 Забрать выигрыш", callback_data="cashout")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def cashout(callback: CallbackQuery, state: FSMContext, data: dict):
    async with AsyncSessionLocal() as session:
        user = await session.execute(select(User).where(User.tg_id == callback.from_user.id))
        user = user.scalar()
        user.balance += data['won']
        await session.commit()

    grid = data['grid']
    opened = data['opened']
    await callback.message.edit_reply_markup(reply_markup=await reveal_grid(grid, opened))
    await callback.message.answer(
        f"🏆 Выигрыш: {data['won']:.2f} ₽\n💰 Баланс: {user.balance:.2f} ₽",
        reply_markup=games_menu()
    )
    await state.clear()

@router.callback_query(MinesStates.PLAYING)
async def process_cell(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    grid = data["grid"]
    opened = data["opened"]
    mines = data["mines"]
    safe = data["safe"]
    bet = data["bet"]
    multiplier = data["multiplier"]

    if callback.data == "cashout":
        if data['won'] <= 0:
            await callback.answer("Нечего забирать!", show_alert=True)
            return
        await cashout(callback, state, data)
        return

    row, col = map(int, callback.data.split("_"))
    if opened[row][col]:
        await callback.answer("Уже открыто!")
        return

    # Анимация
    for i in range(3):
        try:
            await callback.message.edit_text(f"💣 Открываем... {'✨'*(i+1)}", reply_markup=callback.message.reply_markup)
            await asyncio.sleep(0.2)
        except Exception:
            pass

    if grid[row][col] == EMOJI_MINE:
        await show_game_over(callback, state, grid, opened, bet)
        return

    opened[row][col] = True
    safe += 1
    multiplier *= BASE_MULTIPLIER
    won = bet * multiplier

    await state.update_data(opened=opened, safe=safe, multiplier=multiplier, won=won)

    text = (
        f"💣 Мин: {mines}\n"
        f"📈 Открыто: {safe}\n"
        f"🎰 Множитель: x{multiplier:.2f}\n"
        f"💰 Выигрыш: {won:.2f} ₽"
    )

    if safe == GRID_SIZE * GRID_SIZE - mines:
        await cashout(callback, state, await state.get_data())
        return

    try:
        await callback.message.edit_text(text, reply_markup=await render_grid(opened, True))
    except Exception:
        pass

async def show_game_over(callback, state, grid, opened, bet):
    async with AsyncSessionLocal() as session:
        user = await session.execute(select(User).where(User.tg_id == callback.from_user.id))
        user = user.scalar()
        await session.commit()

    # Открываем все
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            opened[i][j] = True

    await callback.message.edit_reply_markup(reply_markup=await reveal_grid(grid, opened))
    await callback.message.answer(
        f"💥 Мина! Вы проиграли {bet:.2f} ₽\n💰 Баланс: {user.balance:.2f} ₽",
        reply_markup=games_menu()
    )
    await state.clear()

async def reveal_grid(grid, opened):
    buttons = []
    for i, row in enumerate(grid):
        btn_row = []
        for j, cell in enumerate(row):
            text = cell if opened[i][j] else EMOJI_HIDDEN  # ИСПРАВЛЕНО!
            btn_row.append(InlineKeyboardButton(text=text, callback_data=" "))
        buttons.append(btn_row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)