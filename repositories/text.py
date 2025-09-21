from typing import Optional, List
import logging
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.text import Text
from core.schemas.text import (
    TextCreateRequest, TextUpdateRequest, 
    TextGetRequest, TextListRequest
)

logger = logging.getLogger(__name__)


class TextRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_text(self, text_data: TextCreateRequest) -> Optional[Text]:
        """
        Create a new text.
        
        Args:
            text_data: Text creation request with user_id, encryption_type, and text
            
        Returns:
            Optional[Text]: Created text model if successful, None otherwise
        """
        logger.info(f"Creating new text for user_id: {text_data.user_id}")
        
        # Create new text
        text = Text(
            user_id=text_data.user_id,
            encryption_type=text_data.encryption_type,
            text=text_data.text,
            is_active=True
        )
        
        self.session.add(text)
        await self.session.commit()
        await self.session.refresh(text)
        
        logger.info(f"Successfully created text with id: {text.id}")
        return text

    async def get_text_by_id(self, text_id: int) -> Optional[Text]:
        """
        Get text by ID.
        
        Args:
            text_id: Text ID
            
        Returns:
            Optional[Text]: Text model if found, None otherwise
        """
        logger.info(f"Getting text by id: {text_id}")
        query = select(Text).where(Text.id == text_id)
        result = await self.session.execute(query)
        text = result.scalar_one_or_none()
        
        if text is None:
            logger.warning(f"Text with id {text_id} not found")
        return text

    async def get_text_by_id_and_user(self, text_id: int, user_id: int) -> Optional[Text]:
        """
        Get text by ID and user ID (for authorization).
        
        Args:
            text_id: Text ID
            user_id: User ID
            
        Returns:
            Optional[Text]: Text model if found and belongs to user, None otherwise
        """
        logger.info(f"Getting text by id: {text_id} for user_id: {user_id}")
        query = select(Text).where(
            and_(
                Text.id == text_id,
                Text.user_id == user_id
            )
        )
        result = await self.session.execute(query)
        text = result.scalar_one_or_none()
        
        if text is None:
            logger.warning(f"Text with id {text_id} not found for user_id {user_id}")
        return text

    async def update_text(self, text_id: int, user_id: int, update_data: TextUpdateRequest) -> Optional[Text]:
        """
        Update text by ID and user ID.
        
        Args:
            text_id: Text ID
            user_id: User ID (for authorization)
            update_data: Update request with fields to update
            
        Returns:
            Optional[Text]: Updated text model if successful, None otherwise
        """
        logger.info(f"Updating text id: {text_id} for user_id: {user_id}")
        
        # Get text and verify ownership
        text = await self.get_text_by_id_and_user(text_id, user_id)
        if text is None:
            logger.warning(f"Text with id {text_id} not found or not owned by user_id {user_id}")
            return None
        
        # Update fields if provided
        if update_data.encryption_type is not None:
            text.encryption_type = update_data.encryption_type
        if update_data.text is not None:
            text.text = update_data.text
        if update_data.is_active is not None:
            text.is_active = update_data.is_active
        
        await self.session.commit()
        await self.session.refresh(text)
        
        logger.info(f"Successfully updated text id: {text_id}")
        return text

    async def delete_text(self, text_id: int, user_id: int) -> bool:
        """
        Delete text by ID and user ID (soft delete by setting is_active=False).
        
        Args:
            text_id: Text ID
            user_id: User ID (for authorization)
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"Deleting text id: {text_id} for user_id: {user_id}")
        
        # Get text and verify ownership
        text = await self.get_text_by_id_and_user(text_id, user_id)
        if text is None:
            logger.warning(f"Text with id {text_id} not found or not owned by user_id {user_id}")
            return False
        
        # Soft delete by setting is_active=False
        text.is_active = False
        await self.session.commit()
        
        logger.info(f"Successfully deleted text id: {text_id}")
        return True

    async def get_user_texts(self, user_id: int, is_active: Optional[bool] = None, 
                           encryption_type: Optional[str] = None) -> List[Text]:
        """
        Get list of texts for a user with optional filters.
        
        Args:
            user_id: User ID
            is_active: Filter by active status (optional)
            encryption_type: Filter by encryption type (optional)
            
        Returns:
            List[Text]: List of text models
        """
        logger.info(f"Getting texts for user_id: {user_id} with filters - is_active: {is_active}, encryption_type: {encryption_type}")
        
        # Build query with filters
        conditions = [Text.user_id == user_id]
        
        if is_active is not None:
            conditions.append(Text.is_active == is_active)
        
        if encryption_type is not None:
            conditions.append(Text.encryption_type == encryption_type)
        
        query = select(Text).where(and_(*conditions)).order_by(Text.created_at.desc())
        result = await self.session.execute(query)
        texts = result.scalars().all()
        
        logger.info(f"Found {len(texts)} texts for user_id: {user_id}")
        return list(texts)

    async def get_all_texts(self) -> List[Text]:
        """
        Get all texts (admin access).
        
        Returns:
            List[Text]: List of all text models
        """
        logger.info("Getting all texts (admin access)")
        
        query = select(Text).order_by(Text.created_at.desc())
        result = await self.session.execute(query)
        texts = result.scalars().all()
        
        logger.info(f"Found {len(texts)} texts total")
        return list(texts)