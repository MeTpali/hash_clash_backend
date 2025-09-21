from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from core.schemas.text import (
    TextCreateRequest, TextCreateResponse,
    TextUpdateRequest, TextUpdateResponse,
    TextDeleteRequest, TextDeleteResponse,
    TextGetRequest, TextGetResponse,
    TextListRequest, TextListResponse
)
from api.deps import get_text_service
from services.text import TextService

router = APIRouter(
    prefix="/texts",
    tags=["texts"],
    responses={401: {"description": "Authentication required"}}
)

@router.post(
    "/",
    response_model=TextCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new text",
    description="Create a new encrypted text",
    responses={
        201: {"description": "Text created successfully"},
        400: {"description": "Invalid text data"},
        500: {"description": "Error creating text"}
    }
)
async def create_text(
    text_data: TextCreateRequest,
    text_service: TextService = Depends(get_text_service)
):
    """
    Create a new encrypted text:
    - Validates text data and encryption type
    - Creates new text record in database
    - Returns creation confirmation with text ID
    - Supports RSA and Grasshopper encryption types
    """
    return await text_service.create_text(text_data)

@router.get(
    "/{text_id}",
    response_model=TextGetResponse,
    summary="Get text by ID",
    description="Get encrypted text by ID (user can only access their own texts)",
    responses={
        200: {"description": "Text retrieved successfully"},
        404: {"description": "Text not found or access denied"},
        400: {"description": "Invalid text ID"}
    }
)
async def get_text(
    text_id: int,
    user_id: int = Query(..., description="User ID for authorization"),
    text_service: TextService = Depends(get_text_service)
):
    """
    Get text by ID:
    - Validates text ID
    - Checks user ownership
    - Returns text data if authorized
    - Includes encryption type and metadata
    """
    return await text_service.get_text(text_id, user_id)

@router.put(
    "/{text_id}",
    response_model=TextUpdateResponse,
    summary="Update text",
    description="Update encrypted text (user can only update their own texts)",
    responses={
        200: {"description": "Text updated successfully"},
        404: {"description": "Text not found or access denied"},
        400: {"description": "Invalid update data"}
    }
)
async def update_text(
    text_id: int,
    user_id: int = Query(..., description="User ID for authorization"),
    update_data: TextUpdateRequest = None,
    text_service: TextService = Depends(get_text_service)
):
    """
    Update text:
    - Validates update data
    - Checks user ownership
    - Updates specified fields only
    - Returns updated text data
    """
    # Устанавливаем text_id из URL в данные обновления
    if update_data is None:
        update_data = TextUpdateRequest(id=text_id)
    else:
        update_data.id = text_id
    
    return await text_service.update_text(text_id, user_id, update_data)

@router.delete(
    "/{text_id}",
    response_model=TextDeleteResponse,
    summary="Delete text",
    description="Delete encrypted text (soft delete, user can only delete their own texts)",
    responses={
        200: {"description": "Text deleted successfully"},
        404: {"description": "Text not found or access denied"},
        400: {"description": "Invalid text ID"}
    }
)
async def delete_text(
    text_id: int,
    user_id: int = Query(..., description="User ID for authorization"),
    text_service: TextService = Depends(get_text_service)
):
    """
    Delete text:
    - Validates text ID
    - Checks user ownership
    - Performs soft delete (sets is_active=False)
    - Returns deletion confirmation
    """
    return await text_service.delete_text(text_id, user_id)

@router.get(
    "/",
    response_model=TextListResponse,
    summary="Get user texts",
    description="Get list of user's encrypted texts with optional filters",
    responses={
        200: {"description": "Texts retrieved successfully"},
        400: {"description": "Invalid filter parameters"}
    }
)
async def get_user_texts(
    user_id: int = Query(..., description="User ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    encryption_type: Optional[str] = Query(None, description="Filter by encryption type (rsa/grasshopper)"),
    text_service: TextService = Depends(get_text_service)
):
    """
    Get user's texts:
    - Returns list of user's texts
    - Supports filtering by active status
    - Supports filtering by encryption type
    - Returns total count and text details
    - Ordered by creation date (newest first)
    """
    return await text_service.get_user_texts(user_id, is_active, encryption_type)

@router.get(
    "/admin/all",
    response_model=TextListResponse,
    summary="Get all texts (Admin)",
    description="Get all encrypted texts (admin access, no ownership check)",
    responses={
        200: {"description": "All texts retrieved successfully"},
        500: {"description": "Error retrieving texts"}
    }
)
async def get_all_texts_admin(
    text_service: TextService = Depends(get_text_service)
):
    """
    Get all texts (Admin access):
    - No ownership check (admin access)
    - Returns all texts from all users
    - Use with caution - admin only endpoint
    """
    return await text_service.get_all_texts_admin()
