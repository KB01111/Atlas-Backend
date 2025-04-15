from loguru import logger
from supabase import Client, create_client

from app.core.config import get_settings


class SupabaseClientError(Exception):
    """Custom exception for Supabase client errors."""
    pass

def get_supabase_client() -> Client:
    """
    Factory for Supabase client. Prepares for async usage and secret retrieval via KeyService.
    Raises SupabaseClientError on failure.
    """
    try:
        settings = get_settings()
        url = settings.SUPABASE_URL
        key = settings.SUPABASE_SERVICE_ROLE_KEY
        # TODO: Integrate KeyService for secret retrieval when ready
        client = create_client(url, key)
        return client
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        raise SupabaseClientError("Could not initialize Supabase client")

# Do NOT create a global supabase client at import time.
# Always use get_supabase_client() when you need the client.
