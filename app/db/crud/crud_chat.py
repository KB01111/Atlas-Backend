from app.db.supabase_client import supabase
from app.models.chat import ChatSessionCreate, ChatMessageCreate
from typing import List, Optional

SESSION_TABLE = "chat_sessions"
MESSAGE_TABLE = "chat_messages"

async def create_session(user_id: str, session: ChatSessionCreate) -> dict:
    data = session.dict()
    data["user_id"] = user_id
    res = supabase.table(SESSION_TABLE).insert(data).execute()
    if res.data:
        return res.data[0]
    raise Exception(res.error)

async def list_sessions(user_id: str) -> List[dict]:
    res = supabase.table(SESSION_TABLE).select("*").eq("user_id", user_id).eq("archived", False).order("created_at", desc=True).execute()
    return res.data or []

async def save_message(chat_session_id: str, message: ChatMessageCreate) -> dict:
    data = message.dict()
    data["chat_session_id"] = chat_session_id
    res = supabase.table(MESSAGE_TABLE).insert(data).execute()
    if res.data:
        return res.data[0]
    raise Exception(res.error)

async def get_messages(chat_session_id: str, limit: int = 50, offset: int = 0) -> List[dict]:
    res = (
        supabase.table(MESSAGE_TABLE)
        .select("*")
        .eq("chat_session_id", chat_session_id)
        .order("timestamp", desc=False)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return res.data or []