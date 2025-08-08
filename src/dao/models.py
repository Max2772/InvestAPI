import os

from sqlalchemy import Column, String, Boolean, DateTime, create_engine, BigInteger
from datetime import datetime, UTC
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'invsetingapibot_users'

    telegram_id = Column(BigInteger, primary_key=True)  # ID пользователя в Telegram
    username = Column(String(50), nullable=True)  # @username (может быть None, если скрыт)
    first_name = Column(String(50), nullable=False)  # Имя
    last_name = Column(String(50), nullable=True)  # Фамилия (может быть None)
    phone = Column(String(20), nullable=True)  # Телефон (если пользователь его предоставит)
    is_admin = Column(Boolean, default=False)  # Админ ли?
    is_active = Column(Boolean, default=True)  # Активен ли аккаунт?
    registered_at = Column(DateTime(timezone=True), default=datetime.now(tz=UTC))  # Дата регистрации

    def __repr__(self):
        return f"<User(id={self.telegram_id}, username='{self.username}')>"


engine = create_engine(
    os.getenv("INVESTINGAPIBOT_DATABASE_URL", "sqlite:///InvestingAPIBot.db"),
    echo=True)