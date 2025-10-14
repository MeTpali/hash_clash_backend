from fastapi import APIRouter, Depends, HTTPException, status
from core.schemas.temp_codes import (
    SendCodeRequest, VerifyCodeRequest, TempCodeResponse
)
from services.temp_codes import TempCodeService
from repositories.temp_codes import TempCodeRepository
from repositories.auth import AuthRepository
from core.models.db_helper import DatabaseHelper
from api.deps import get_temp_code_service

router = APIRouter(
    prefix="/temp-codes",
    tags=["temp-codes"],
    responses={400: {"description": "Bad request"}}
)

@router.post(
    "/send-login-code",
    response_model=TempCodeResponse,
    summary="Send login confirmation code",
    description="Send 6-digit confirmation code to user's email for login",
    responses={
        200: {"description": "Code sent successfully"},
        400: {"description": "User not found or no email set"},
        500: {"description": "Error sending email"}
    }
)
async def send_login_code(
    request: SendCodeRequest,
    temp_code_service: TempCodeService = Depends(get_temp_code_service)
):
    """
    Отправить код подтверждения входа:
    - Проверяет существование пользователя
    - Генерирует 6-значный код
    - Отправляет код на email пользователя
    - Код действителен 10 минут
    """
    return await temp_code_service.send_login_code(request)


@router.post(
    "/verify-login-code",
    response_model=TempCodeResponse,
    summary="Verify login confirmation code",
    description="Verify 6-digit confirmation code for login",
    responses={
        200: {"description": "Code verified successfully"},
        400: {"description": "Invalid or expired code"}
    }
)
async def verify_login_code(
    request: VerifyCodeRequest,
    temp_code_service: TempCodeService = Depends(get_temp_code_service)
):
    """
    Проверить код подтверждения входа:
    - Проверяет валидность кода
    - Проверяет срок действия
    - Отмечает код как использованный
    """
    return await temp_code_service.verify_login_code(request)


@router.post(
    "/cleanup-expired",
    summary="Cleanup expired codes",
    description="Remove all expired temporary codes from database",
    responses={
        200: {"description": "Cleanup completed successfully"}
    }
)
async def cleanup_expired_codes(
    temp_code_service: TempCodeService = Depends(get_temp_code_service)
):
    """
    Очистить истекшие коды:
    - Удаляет все коды с истекшим сроком действия
    - Возвращает количество удаленных кодов
    """
    deleted_count = await temp_code_service.cleanup_expired_codes()
    return {"message": f"Cleaned up {deleted_count} expired codes", "deleted_count": deleted_count}
