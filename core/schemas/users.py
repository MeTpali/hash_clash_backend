from datetime import datetime
from pydantic import EmailStr
from .base import BaseSchema


class UserResponse(BaseSchema):
    id: int
    username: str
    email: EmailStr | None = None
    user_type: str
    is_email_confirmed: bool
    is_totp_confirmed: bool
    created_at: datetime | None = None
    is_active: bool
