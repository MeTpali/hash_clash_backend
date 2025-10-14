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


class TempCode(Base):
    __tablename__ = "temp_codes"

    # id кода обязательный
    id = Column(Integer, primary_key=True, index=True)
    # id пользователя, для которого создан код обязательный
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # Сам код обязательный
    code = Column(String(6), nullable=False)
    # Тип кода (email_confirmation, login_confirmation, etc.) обязательный
    code_type = Column(String(50), nullable=False)
    # Время создания обязательный
    created_at = Column(DateTime, default=lambda: datetime.utcnow(), nullable=False)
    # Время истечения обязательный
    expires_at = Column(DateTime, nullable=False)
    # Использован ли код обязательное, по умолчанию False
    is_used = Column(Boolean, default=False, nullable=False)
    # Активен ли код обязательное, по умолчанию True
    is_active = Column(Boolean, default=True, nullable=False)

    # Связь с пользователем
    user = relationship("User", back_populates="temp_codes")
