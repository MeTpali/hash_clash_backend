from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base


# 1. Модель User
class User(Base):
    __tablename__ = "users"

    # id пользователя обязательный
    id = Column(Integer, primary_key=True, index=True)
    # Имя пользователя (логин) обязательный
    username = Column(String, unique=True, nullable=False)
    # Почта опциональная
    email = Column(String, unique=True, nullable=True)
    # Тип пользователя обязательный (user, admin)
    user_type = Column(String, nullable=False)
    # Hash пароля обязательный
    password_hash = Column(String, nullable=False)
    # Подтверждение почты обязательное, по умолчанию False
    is_email_confirmed = Column(Boolean, default=False, nullable=False)
    # Ключ TOTP опциональный
    totp_key = Column(String, nullable=True)
    # Подтверждение TOTP опциональное, по умолчанию False
    is_totp_confirmed = Column(Boolean, default=False, nullable=False)
    # Время создания обязательный
    created_at = Column(DateTime, default=lambda: datetime.now())
    # Активный ли пользователь обязательное
    is_active = Column(Boolean, default=True, nullable=False)

    # Связь с текстами
    texts = relationship("Text", back_populates="user")
    # Связь с временными кодами
    temp_codes = relationship("TempCode", back_populates="user")