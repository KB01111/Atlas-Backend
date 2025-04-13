from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from app.core.security import get_current_user_id
from app.services.key_service import (
    store_api_key,
    list_api_keys,
    delete_api_key,
)
router = APIRouter(prefix="/keys", tags=["keys"])

class APIKeyIn(BaseModel):
    service: str
    key: str

class APIKeyMetaOut(BaseModel):
    id: str
    service: str
    created_at: Optional[str]
    last_used_at: Optional[str]

@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_key(
    key_in: APIKeyIn,
    user_id: str = Depends(get_current_user_id)
):
    await store_api_key(user_id, key_in.service, key_in.key)
    return {"status": "ok"}

@router.get("/", response_model=List[APIKeyMetaOut])
async def get_keys(
    user_id: str = Depends(get_current_user_id)
):
    return await list_api_keys(user_id)

@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_key(
    key_id: str,
    user_id: str = Depends(get_current_user_id)
):
    await delete_api_key(user_id, key_id)
    return