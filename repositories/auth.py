from typing import Optional
import logging
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.users import User
from core.schemas.auth import RegisterRequest, AuthRequest, AuthResponse, RegisterResponse
from core.auth.password import get_password_hash, verify_password
from core.auth.totp import verify_totp

logger = logging.getLogger(__name__)

class AuthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _hash_password(self, password: str) -> str:
        """Hash password using the same method as UserRepository"""
        logger.info(f"Hashing password for authentication")
        hashed = get_password_hash(password)
        logger.info(f"Generated hash: {hashed}")
        return hashed

    async def authenticate_user(self, auth_data: AuthRequest) -> Optional[User]:
        """
        Authenticate user by login (username or email) and password.
        
        Args:
            auth_data: Authentication request with login and password
            
        Returns:
            Optional[User]: User model if authentication successful, None otherwise
        """
        logger.info(f"Authenticating user with login: {auth_data.login}")
        
        # Search by username or email
        query = select(User).where(
            or_(
                User.username == auth_data.login,
                User.email == auth_data.login
            ),
            User.is_active == True
        )
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        
        if user is None:
            logger.warning(f"User with login {auth_data.login} not found")
            return None
            
        # Verify password
        if not verify_password(auth_data.password, user.password_hash):
            logger.warning(f"Invalid password for user {auth_data.login}")
            return None
            
        logger.info(f"Successfully authenticated user {auth_data.login}")
        return user

    async def register_user(self, register_data: RegisterRequest, user_type: str = "user") -> Optional[User]:
        """
        Register a new user.
        
        Args:
            register_data: Registration request with login and password
            user_type: Type of user to create (default: "user")
            
        Returns:
            Optional[User]: Created user model if successful, None if user already exists
        """
        logger.info(f"Registering new user with login: {register_data.login}")
        
        # Check if user already exists
        existing_user = await self.get_user_by_login(register_data.login)
        if existing_user:
            logger.warning(f"User with login {register_data.login} already exists")
            return None
            
        # Hash password
        hashed_password = self._hash_password(register_data.password)
        
        # Create new user
        user = User(
            username=register_data.login,
            user_type=user_type,
            password_hash=hashed_password,
            email=None,  # Email is optional
            is_email_confirmed=False,
            totp_key=None,
            is_totp_confirmed=False
        )
        
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        
        logger.info(f"Successfully registered user with id: {user.id}")
        return user

    async def get_user_by_login(self, login: str) -> Optional[User]:
        """
        Get user by login (username or email).
        
        Args:
            login: Username or email
            
        Returns:
            Optional[User]: User model if found, None otherwise
        """
        logger.info(f"Getting user by login: {login}")
        query = select(User).where(
            or_(
                User.username == login,
                User.email == login
            ),
            User.is_active == True
        )
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        
        if user is None:
            logger.warning(f"User with login {login} not found")
        return user

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID for authentication purposes.
        
        Args:
            user_id: User ID
            
        Returns:
            Optional[User]: User model if found, None otherwise
        """
        logger.info(f"Getting user by id: {user_id}")
        query = select(User).where(User.id == user_id, User.is_active == True)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        
        if user is None:
            logger.warning(f"User with id {user_id} not found")
        return user

    async def update_user_password(self, user_id: int, new_password: str) -> bool:
        """
        Update user password.
        
        Args:
            user_id: User ID
            new_password: New password
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"Updating password for user id: {user_id}")
        query = select(User).where(User.id == user_id, User.is_active == True)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        
        if user is None:
            logger.warning(f"User with id {user_id} not found for password update")
            return False
            
        user.password_hash = self._hash_password(new_password)
        await self.session.commit()
        
        logger.info(f"Successfully updated password for user id: {user_id}")
        return True

    async def enable_totp(self, user_id: int, totp_key: str) -> bool:
        """
        Enable TOTP for user.
        
        Args:
            user_id: User ID
            totp_key: TOTP secret key
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"Enabling TOTP for user id: {user_id}")
        query = select(User).where(User.id == user_id, User.is_active == True)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        
        if user is None:
            logger.warning(f"User with id {user_id} not found for TOTP enable")
            return False
            
        user.totp_key = totp_key
        user.is_totp_confirmed = True
        await self.session.commit()
        
        logger.info(f"Successfully enabled TOTP for user id: {user_id}")
        return True

    async def disable_totp(self, user_id: int) -> bool:
        """
        Disable TOTP for user.
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"Disabling TOTP for user id: {user_id}")
        query = select(User).where(User.id == user_id, User.is_active == True)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        
        if user is None:
            logger.warning(f"User with id {user_id} not found for TOTP disable")
            return False
            
        user.totp_key = None
        user.is_totp_confirmed = False
        await self.session.commit()
        
        logger.info(f"Successfully disabled TOTP for user id: {user_id}")
        return True

    async def verify_totp(self, user_id: int, totp_code: str) -> bool:
        """
        Verify TOTP code for user.
        
        Args:
            user_id: User ID
            totp_code: TOTP code to verify
            
        Returns:
            bool: True if TOTP is valid, False otherwise
        """
        logger.info(f"Verifying TOTP for user id: {user_id}")
        query = select(User).where(User.id == user_id, User.is_active == True)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        
        if user is None or not user.totp_key:
            logger.warning(f"User with id {user_id} not found or TOTP not enabled")
            return False
            
        # Verify TOTP code using the actual TOTP verification
        is_valid = verify_totp(user.totp_key, totp_code)
        
        if is_valid:
            logger.info(f"TOTP verification successful for user id: {user_id}")
        else:
            logger.warning(f"TOTP verification failed for user id: {user_id}")
            
        return is_valid