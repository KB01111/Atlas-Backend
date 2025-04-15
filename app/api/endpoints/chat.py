from typing import List

from fastapi import APIRouter, Depends, Query, status

from app.core.security import get_current_user_id
from app.db.crud.crud_chat import (
    create_session,
    get_messages,
    list_sessions,
)
from app.models.chat import ChatMessageOut, ChatSessionCreate, ChatSessionOut

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "/sessions",
    response_model=ChatSessionOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_session_endpoint(
    session: ChatSessionCreate, user_id: str = Depends(get_current_user_id)
):
    db_session = await create_session(user_id, session)
    return db_session


@router.get("/sessions", response_model=List[ChatSessionOut])
async def list_sessions_endpoint(user_id: str = Depends(get_current_user_id)):
    sessions = await list_sessions(user_id)
    return sessions


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageOut])
async def get_messages_endpoint(
    session_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user_id),
):
    # (Optional: check session ownership here)
    messages = await get_messages(session_id, limit=limit, offset=offset)
    return messages
