from fastapi import APIRouter
from api.v1.endpoints import (
    auth,
    text,
    users,
    temp_codes
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(text.router)
api_router.include_router(users.router)
api_router.include_router(temp_codes.router)