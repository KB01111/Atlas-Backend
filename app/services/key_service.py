from datetime import datetime
from typing import Optional

from app.db.supabase_client import get_supabase_client

KEYS_TABLE = "user_api_keys"

class KeyService:
    """
    Service for encrypting and decrypting plugin configuration blobs.
    Encryption is currently a stub (no-op).
    """
    @staticmethod
    def encrypt_config(blob: str, user_id: str) -> str:
        """Stub for encrypting plugin config. Returns blob unchanged."""
        # TODO: Implement real encryption
        return blob

    @staticmethod
    def decrypt_config(blob: str, user_id: str) -> str:
        """Stub for decrypting plugin config. Returns blob unchanged."""
        # TODO: Implement real decryption
        return blob

async def store_api_key(user_id: str, service: str, key: str) -> None:
    """Store an API key for a user and service in Supabase."""
    data = {
        "user_id": user_id,
        "service": service,
        "created_at": datetime.utcnow().isoformat(),
    }
    supabase = get_supabase_client()
    res = supabase.table(KEYS_TABLE).upsert(data, on_conflict=["user_id", "service"]).execute()
    if res.error:
        raise Exception(res.error)

async def get_api_key(user_id: str, service: str) -> Optional[str]:
    """Stub: Always returns None."""
    return None

async def list_api_keys(user_id: str) -> list[dict]:
    """List all API keys for a user from Supabase."""
    supabase = get_supabase_client()
    res = supabase.table(KEYS_TABLE).select("id,service,created_at,last_used_at").eq("user_id", user_id).execute()
    return res.data or []

async def delete_api_key(user_id: str, key_id: str) -> None:
    """Delete an API key for a user from Supabase."""
    supabase = get_supabase_client()
    res = supabase.table(KEYS_TABLE).delete().eq("user_id", user_id).eq("id", key_id).execute()
    if res.error:
        raise Exception(res.error)
