from typing import List

from loguru import logger

from app.db.supabase_client import SupabaseClientError, get_supabase_client
from app.models.chat import ChatMessageCreate, ChatSessionCreate

# TODO: When async supabase client is available, refactor these methods to async/await.
# TODO: Integrate KeyService for secure secret handling and Vault integration when ready.

SESSION_TABLE = "chat_sessions"
MESSAGE_TABLE = "chat_messages"

# Replace all usages of 'supabase' with the result of get_supabase_client() where needed.
# For example:
# supabase = get_supabase_client()

async def create_session(user_id: str, session: ChatSessionCreate) -> dict:
    """
    Create a new chat session for a user.
    Raises SupabaseClientError on failure.
    """
    data = session.dict()
    data["user_id"] = user_id
    supabase = get_supabase_client()
    try:
        res = supabase.table(SESSION_TABLE).insert(data).execute()
        if res.data:
            return res.data[0]
        logger.error(f"Supabase insert error: {res.error}")
        raise SupabaseClientError(res.error)
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        raise SupabaseClientError("Failed to create chat session")

async def list_sessions(user_id: str) -> List[dict]:
    """
    List all non-archived chat sessions for a user, ordered by creation time (desc).
    Returns empty list if none found.
    Raises SupabaseClientError on failure.
    """
    supabase = get_supabase_client()
    try:
        res = supabase.table(SESSION_TABLE).select("*").eq("user_id", user_id).eq("archived", False).order("created_at", desc=True).execute()
        return res.data or []
    except Exception as e:
        logger.error(f"Error listing chat sessions: {e}")
        raise SupabaseClientError("Failed to list chat sessions")

async def save_message(chat_session_id: str, message: ChatMessageCreate) -> dict:
    """
    Save a chat message to a session.
    Raises SupabaseClientError on failure.
    """
    data = message.dict()
    data["chat_session_id"] = chat_session_id
    supabase = get_supabase_client()
    try:
        res = supabase.table(MESSAGE_TABLE).insert(data).execute()
        if res.data:
            return res.data[0]
        logger.error(f"Supabase insert error: {res.error}")
        raise SupabaseClientError(res.error)
    except Exception as e:
        logger.error(f"Error saving chat message: {e}")
        raise SupabaseClientError("Failed to save chat message")

async def get_messages(chat_session_id: str, limit: int = 50, offset: int = 0) -> List[dict]:
    """
    Retrieve messages for a chat session, paginated.
    Returns empty list if none found.
    Raises SupabaseClientError on failure.
    """
    supabase = get_supabase_client()
    try:
        res = (
            supabase.table(MESSAGE_TABLE)
            .select("*")
            .eq("chat_session_id", chat_session_id)
            .order("timestamp", desc=False)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return res.data or []
    except Exception as e:
        logger.error(f"Error retrieving chat messages: {e}")
        raise SupabaseClientError("Failed to retrieve chat messages")
