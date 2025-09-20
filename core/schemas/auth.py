from pydantic import EmailStr
from .base import BaseSchema

class RegisterRequest(BaseSchema):
    login: str
    password: str

class RegisterResponse(BaseSchema):
    user_id: int
    message: str | None = None

class AuthRequest(BaseSchema):
    login: str
    password: str

class AuthResponse(BaseSchema):
    user_id: int
    message: str | None = None
    email: EmailStr | None = None
    totp_enabled: bool | None = None

class TotpGenerateRequest(BaseSchema):
    user_id: int

class TotpGenerateResponse(BaseSchema):
    user_id: int
    totp_uri: str
    message: str | None = None

class TotpVerifyRequest(BaseSchema):
    user_id: int
    code: str

class TotpVerifyResponse(BaseSchema):
    user_id: int
    verified: bool
    message: str | None = None
