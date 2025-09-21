from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base


# Модель Text для загружаемого текста
class Text(Base):
    __tablename__ = "texts"

    # id текста обязательный
    id = Column(Integer, primary_key=True, index=True)
    # id пользователя, который загрузил текст обязательный
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # Тип шифрования (rsa/grasshopper) обязательный
    encryption_type = Column(String, nullable=False)
    # Сам текст обязательный
    text = Column(String, nullable=False)
    # Время создания обязательный
    created_at = Column(DateTime, default=lambda: datetime.now(), nullable=False)
    # Активен ли текст обязательное
    is_active = Column(Boolean, default=True, nullable=False)

    # Связь с пользователем
    user = relationship("User", back_populates="texts")
