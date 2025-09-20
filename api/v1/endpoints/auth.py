from fastapi import APIRouter, Depends, HTTPException, status
from core.schemas.auth import (
    RegisterRequest, AuthRequest, AuthResponse, RegisterResponse,
    TotpGenerateRequest, TotpGenerateResponse, TotpVerifyRequest, TotpVerifyResponse
)
from api.deps import get_auth_service
from services.auth import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"description": "Authentication failed"}}
)

@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Authenticate user",
    description="Authenticate user with login and password",
    responses={
        200: {"description": "Authentication successful"},
        401: {"description": "Invalid credentials"},
        400: {"description": "Invalid request data"}
    }
)
async def login(
    auth_data: AuthRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate user with login and password:
    - Validates user credentials
    - Returns authentication result with user info
    - Supports both username and email as login
    """
    return await auth_service.authenticate_user(auth_data)

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user in the system",
    responses={
        201: {"description": "User registered successfully"},
        400: {"description": "Invalid registration data or user already exists"}
    }
)
async def register(
    register_data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user:
    - Validates registration data
    - Checks for existing users
    - Creates new user account
    - Returns registration confirmation
    """
    return await auth_service.register_user(register_data)

@router.post(
    "/totp/generate",
    response_model=TotpGenerateResponse,
    summary="Generate TOTP for user",
    description="Generate TOTP secret and QR code URI for user",
    responses={
        200: {"description": "TOTP generated successfully"},
        404: {"description": "User not found"},
        500: {"description": "Error saving TOTP key"}
    }
)
async def generate_totp(
    request: TotpGenerateRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Generate TOTP for user:
    - Creates new TOTP secret
    - Saves secret to database
    - Returns QR code URI for authenticator app
    - Enables TOTP for the user
    """
    return await auth_service.generate_totp(request)

@router.post(
    "/totp/verify",
    response_model=TotpVerifyResponse,
    summary="Verify TOTP code",
    description="Verify TOTP code for user",
    responses={
        200: {"description": "TOTP verification completed"},
        400: {"description": "TOTP not configured or invalid code"},
        404: {"description": "User not found"}
    }
)
async def verify_totp(
    request: TotpVerifyRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Verify TOTP code for user:
    - Validates TOTP code against user's secret
    - Returns verification result
    - Supports time window tolerance
    """
    return await auth_service.verify_totp(request)
