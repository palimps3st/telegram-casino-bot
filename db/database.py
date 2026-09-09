# db/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .models import Base, User

async def create_db_and_tables():
    engine = create_async_engine("sqlite+aiosqlite:///users.db", echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Создает таблицы
    return engine

async_engine = create_async_engine("sqlite+aiosqlite:///users.db", echo=True)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, expire_on_commit=False, class_=AsyncSession
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session