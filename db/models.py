from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True)
    is_blocked = Column(Boolean, default=False)
    login = Column(String(50), unique=True)
    password = Column(String(100))
    balance = Column(Float, default=0.0)
    subscription_end = Column(DateTime, nullable=True)
    current_bet = Column(Float, default=0.0)
    last_roulette_spin = Column(DateTime, nullable=True)

class Coupon(Base):
    __tablename__ = "coupons"
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True)
    uses_left = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    days_added = Column(Integer)  # Количество дней для продления подписки
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

class GameSettings(Base):
    __tablename__ = "game_settings"
    id = Column(Integer, primary_key=True)
    game_name = Column(String(50), unique=True)
    multiplier = Column(Float, default=1.0)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    type = Column(String(20))  # 'topup' или 'purchase'
    created_at = Column(DateTime, default=datetime.now)
