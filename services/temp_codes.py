import secrets
import string
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import HTTPException, status
from repositories.temp_codes import TempCodeRepository
from repositories.auth import AuthRepository
from core.schemas.temp_codes import (
    SendCodeRequest, VerifyCodeRequest, TempCodeResponse
)
from core.utils.email import send_email
from core.utils.templates import load_html_template
from core.config import settings
import logging

logger = logging.getLogger(__name__)


class TempCodeService:
    def __init__(self, temp_code_repository: TempCodeRepository, auth_repository: AuthRepository):
        self.temp_code_repository = temp_code_repository
        self.auth_repository = auth_repository

    def generate_code(self, length: int = 6) -> str:
        """
        Генерирует случайный числовой код заданной длины.
        
        Args:
            length: Длина кода
            
        Returns:
            str: Сгенерированный код
        """
        return ''.join(secrets.choice(string.digits) for _ in range(length))

    async def send_login_code(self, request: SendCodeRequest) -> TempCodeResponse:
        """
        Отправить код для входа в систему.
        
        Args:
            request: Запрос с ID пользователя
            
        Returns:
            TempCodeResponse: Результат отправки
        """
        logger.info(f"Sending login code for user id: {request.user_id}")
        
        # Проверяем, существует ли пользователь
        user = await self.auth_repository.get_user_by_id(request.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        if not user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="У пользователя не указана почта"
            )
        
        # Деактивируем предыдущие коды входа
        await self.temp_code_repository.deactivate_user_codes(request.user_id, "login_confirmation")
        
        # Генерируем новый код
        code = self.generate_code()
        expires_minutes = 10
        
        # Создаем временный код
        temp_code = await self.temp_code_repository.create_temp_code(
            user_id=request.user_id,
            code=code,
            code_type="login_confirmation",
            expires_minutes=expires_minutes
        )
        
        # Загружаем HTML шаблон письма
        email_body = load_html_template(
            "email_confirmation_code.html",
            code=code,
            expires_minutes=expires_minutes,
            year=datetime.now().year,
            static_url=settings.STATIC_URL
        )
        
        # Отправляем письмо
        success = send_email(
            to_email=user.email,
            subject="Код подтверждения входа | Hash Clash",
            body=email_body
        )
        
        if not success:
            # Если письмо не отправилось, удаляем код
            temp_code.is_active = False
            await self.temp_code_repository.session.commit()
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка отправки письма"
            )
        
        logger.info(f"Login code sent successfully for user {request.user_id}")
        
        return TempCodeResponse(
            success=True,
            message="Код отправлен на вашу почту",
            expires_at=temp_code.expires_at
        )

    async def verify_login_code(self, request: VerifyCodeRequest) -> TempCodeResponse:
        """
        Проверить код для входа в систему.
        
        Args:
            request: Запрос с кодом
            
        Returns:
            TempCodeResponse: Результат проверки
        """
        logger.info(f"Verifying login code for user id: {request.user_id}")
        
        # Ищем валидный код
        temp_code = await self.temp_code_repository.get_valid_code(
            user_id=request.user_id,
            code=request.code,
            code_type="login_confirmation"
        )
        
        if not temp_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный или истекший код"
            )
        
        # Отмечаем код как использованный
        await self.temp_code_repository.mark_code_as_used(temp_code)
        
        logger.info(f"Login code verified successfully for user {request.user_id}")
        
        return TempCodeResponse(
            success=True,
            message="Код подтвержден успешно"
        )

    async def cleanup_expired_codes(self) -> int:
        """
        Очистить истекшие коды.
        
        Returns:
            int: Количество удаленных кодов
        """
        return await self.temp_code_repository.cleanup_expired_codes()
