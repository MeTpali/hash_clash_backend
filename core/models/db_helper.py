from typing import AsyncGenerator
from asyncio import current_task
import logging

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
    AsyncSession,
)
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlalchemy import text

from core.config import settings

logger = logging.getLogger(__name__)

class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
            poolclass=AsyncAdaptedQueuePool,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True,  # Enable connection testing
            connect_args={
                "ssl": "require",
                "command_timeout": 60,  # 60 second timeout
            },
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def get_scoped_session(self):
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )
        return session

    async def session_dependency(self) -> AsyncGenerator[AsyncSession, None]:
        session = self.session_factory()
        try:
            # Test the connection
            await session.execute(text("SELECT 1"))
            yield session
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            await session.close()
            raise
        finally:
            await session.close()


db_helper = DatabaseHelper(
    url=settings.DATABASE_URL,
    echo=settings.DB_ECHO,
)
