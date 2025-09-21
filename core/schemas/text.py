from datetime import datetime
from pydantic import BaseModel
from .base import BaseSchema


class TextCreateRequest(BaseSchema):
    """Схема для создания нового текста"""
    user_id: int
    encryption_type: str  # rsa или grasshopper
    text: str


class TextCreateResponse(BaseSchema):
    """Схема ответа при создании текста"""
    id: int
    user_id: int
    encryption_type: str
    created_at: datetime
    message: str | None = None


class TextUpdateRequest(BaseSchema):
    """Схема для обновления текста"""
    id: int
    encryption_type: str | None = None
    text: str | None = None
    is_active: bool | None = None


class TextUpdateResponse(BaseSchema):
    """Схема ответа при обновлении текста"""
    id: int
    user_id: int
    encryption_type: str
    text: str
    is_active: bool
    created_at: datetime
    message: str | None = None


class TextDeleteRequest(BaseSchema):
    """Схема для удаления текста"""
    id: int


class TextDeleteResponse(BaseSchema):
    """Схема ответа при удалении текста"""
    id: int
    message: str | None = None


class TextGetRequest(BaseSchema):
    """Схема для получения текста"""
    id: int


class TextGetResponse(BaseSchema):
    """Схема ответа при получении текста"""
    id: int
    user_id: int
    encryption_type: str
    text: str
    is_active: bool
    created_at: datetime


class TextListRequest(BaseSchema):
    """Схема для получения списка текстов пользователя"""
    user_id: int
    is_active: bool | None = None  # фильтр по активности
    encryption_type: str | None = None  # фильтр по типу шифрования


class TextListResponse(BaseSchema):
    """Схема ответа при получении списка текстов"""
    texts: list[TextGetResponse]
    total_count: int
    message: str | None = None
