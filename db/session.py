from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.db_helper import db_helper

async_session = db_helper.session_factory

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close() 