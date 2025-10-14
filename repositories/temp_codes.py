from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from datetime import datetime, timezone, timedelta
from typing import Optional
from core.models.temp_codes import TempCode
from core.models.users import User
import logging

logger = logging.getLogger(__name__)


class TempCodeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_temp_code(self, user_id: int, code: str, code_type: str, expires_minutes: int = 10) -> TempCode:
        """
        Создать новый временный код.
        
        Args:
            user_id: ID пользователя
            code: 6-значный код
            code_type: Тип кода
            expires_minutes: Время жизни в минутах
            
        Returns:
            TempCode: Созданный код
        """
        expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)
        
        temp_code = TempCode(
            user_id=user_id,
            code=code,
            code_type=code_type,
            expires_at=expires_at
        )
        
        self.session.add(temp_code)
        await self.session.commit()
        await self.session.refresh(temp_code)
        
        logger.info(f"Created temp code for user {user_id}, type: {code_type}")
        return temp_code

    async def get_valid_code(self, user_id: int, code: str, code_type: str) -> Optional[TempCode]:
        """
        Получить валидный код для пользователя.
        
        Args:
            user_id: ID пользователя
            code: Код для проверки
            code_type: Тип кода
            
        Returns:
            TempCode или None если код не найден/невалиден
        """
        now = datetime.utcnow()
        
        query = select(TempCode).where(
            and_(
                TempCode.user_id == user_id,
                TempCode.code == code,
                TempCode.code_type == code_type,
                TempCode.is_active == True,
                TempCode.is_used == False,
                TempCode.expires_at > now
            )
        )
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def mark_code_as_used(self, temp_code: TempCode) -> None:
        """
        Отметить код как использованный.
        
        Args:
            temp_code: Код для отметки
        """
        temp_code.is_used = True
        await self.session.commit()
        
        logger.info(f"Marked temp code {temp_code.id} as used")

    async def cleanup_expired_codes(self) -> int:
        """
        Удалить все истекшие коды.
        
        Returns:
            int: Количество удаленных кодов
        """
        now = datetime.utcnow()
        
        query = delete(TempCode).where(
            and_(
                TempCode.expires_at < now,
                TempCode.is_active == True
            )
        )
        
        result = await self.session.execute(query)
        await self.session.commit()
        
        deleted_count = result.rowcount
        logger.info(f"Cleaned up {deleted_count} expired temp codes")
        return deleted_count

    async def deactivate_user_codes(self, user_id: int, code_type: str) -> int:
        """
        Деактивировать все активные коды пользователя определенного типа.
        
        Args:
            user_id: ID пользователя
            code_type: Тип кода
            
        Returns:
            int: Количество деактивированных кодов
        """
        query = select(TempCode).where(
            and_(
                TempCode.user_id == user_id,
                TempCode.code_type == code_type,
                TempCode.is_active == True,
                TempCode.is_used == False
            )
        )
        
        result = await self.session.execute(query)
        codes = result.scalars().all()
        
        for code in codes:
            code.is_active = False
        
        await self.session.commit()
        
        deactivated_count = len(codes)
        logger.info(f"Deactivated {deactivated_count} temp codes for user {user_id}, type: {code_type}")
        return deactivated_count
