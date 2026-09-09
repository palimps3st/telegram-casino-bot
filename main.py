import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from db.database import create_db_and_tables
from settings import BOT_TOKEN
from bot.middlewares.block_check import BlockCheckMiddleware
from bot.handlers import setup_handlers

async def main():
    await create_db_and_tables()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    setup_handlers(dp)
    dp.message.middleware(BlockCheckMiddleware())
    dp.callback_query.middleware(BlockCheckMiddleware())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())