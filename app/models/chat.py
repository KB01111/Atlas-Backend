from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

class SessionParticipant(BaseModel):
    user_id: str
    role: Optional[str] = "user"

class ChatSessionBase(BaseModel):
    name: Optional[str] = None
    agent_id: Optional[str] = None
    participants: Optional[List[SessionParticipant]] = []
    archived: Optional[bool] = False

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionOut(ChatSessionBase):
    id: str
    user_id: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class ChatMessageBase(BaseModel):
    content: str
    sender_id: str
    sender_type: str  # "user", "agent", or "system"
    metadata: Optional[Any] = None

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageOut(ChatMessageBase):
    id: str
    chat_session_id: str
    timestamp: datetime

    class Config:
        orm_mode = True