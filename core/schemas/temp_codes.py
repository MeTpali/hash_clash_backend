from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from core.schemas.base import BaseSchema


class TempCodeCreate(BaseSchema):
    """Схема для создания временного кода"""
    user_id: int = Field(..., description="ID пользователя")
    code_type: str = Field(..., description="Тип кода (email_confirmation, login_confirmation, etc.)")
    expires_minutes: int = Field(default=10, description="Время жизни кода в минутах")


class TempCodeVerify(BaseSchema):
    """Схема для проверки временного кода"""
    user_id: int = Field(..., description="ID пользователя")
    code: str = Field(..., min_length=6, max_length=6, description="6-значный код")
    code_type: str = Field(..., description="Тип кода")


class TempCodeResponse(BaseSchema):
    """Схема ответа для временного кода"""
    success: bool = Field(..., description="Успешность операции")
    message: str = Field(..., description="Сообщение о результате")
    expires_at: Optional[datetime] = Field(None, description="Время истечения кода")


class SendCodeRequest(BaseSchema):
    """Схема запроса для отправки кода"""
    user_id: int = Field(..., description="ID пользователя")


class VerifyCodeRequest(BaseSchema):
    """Схема запроса для проверки кода"""
    user_id: int = Field(..., description="ID пользователя")
    code: str = Field(..., min_length=6, max_length=6, description="6-значный код")
