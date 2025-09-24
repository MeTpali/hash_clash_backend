from fastapi import APIRouter, Depends
from api.deps import get_auth_service
from services.auth import AuthService
from core.schemas.users import UserResponse

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by id",
    description="Get user details by user ID",
    responses={
        200: {"description": "User found"},
        404: {"description": "User not found"}
    }
)
async def get_user_by_id(user_id: int, auth_service: AuthService = Depends(get_auth_service)):
    user = await auth_service.get_user_by_id(user_id)
    return user
