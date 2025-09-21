from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from repositories.auth import AuthRepository
from repositories.text import TextRepository

from services.auth import AuthService
from services.text import TextService

# Repositories
async def get_auth_repository(db: AsyncSession = Depends(get_async_session)) -> AuthRepository:
    return AuthRepository(db)

async def get_text_repository(db: AsyncSession = Depends(get_async_session)) -> TextRepository:
    return TextRepository(db)

# Services
async def get_auth_service(
    auth_repository: AuthRepository = Depends(get_auth_repository)
) -> AuthService:
    return AuthService(auth_repository)

async def get_text_service(
    text_repository: TextRepository = Depends(get_text_repository)
) -> TextService:
    return TextService(text_repository)
