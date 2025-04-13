from app.db.supabase_client import supabase
from typing import List, Optional
from datetime import datetime
import base64
import os

KEYS_TABLE = "user_api_keys"

def _encrypt_key(key: str) -> str:
    # Simple base64 "encryption" for demo; replace with real encryption or Supabase Vault in production
    return base64.b64encode(key.encode()).decode()

def _decrypt_key(enc: str) -> str:
    return base64.b64decode(enc.encode()).decode()

async def store_api_key(user_id: str, service: str, key: str):
    enc_key = _encrypt_key(key)
    data = {
        "user_id": user_id,
        "service": service,
        "key_enc": enc_key,
        "created_at": datetime.utcnow().isoformat()
    }
    # Upsert: one key per user/service
    res = supabase.table(KEYS_TABLE).upsert(data, on_conflict=["user_id", "service"]).execute()
    if res.error:
        raise Exception(res.error)

async def list_api_keys(user_id: str) -> List[dict]:
    res = supabase.table(KEYS_TABLE).select("id,service,created_at,last_used_at").eq("user_id", user_id).execute()
    return res.data or []

async def delete_api_key(user_id: str, key_id: str):
    res = supabase.table(KEYS_TABLE).delete().eq("user_id", user_id).eq("id", key_id).execute()
    if res.error:
        raise Exception(res.error)

async def get_api_key(user_id: str, service: str) -> Optional[str]:
    res = supabase.table(KEYS_TABLE).select("key_enc").eq("user_id", user_id).eq("service", service).single().execute()
    if res.data and res.data.get("key_enc"):
        return _decrypt_key(res.data["key_enc"])
    return None