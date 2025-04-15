from typing import Optional

from loguru import logger

from app.db.supabase_client import SupabaseClientError, get_supabase_client
from app.models.plugin import (
    PluginConfigurationCreate,
    PluginConfigurationUpdate,
)
from app.services.key_service import KeyService

PLUGIN_TABLE = "plugin_configurations"

class PluginServiceError(Exception):
    """Custom exception for PluginService errors."""
    pass

class PluginService:
    @staticmethod
    async def create_plugin_config(user_id: str, config: PluginConfigurationCreate) -> dict:
        """
        Create a new plugin configuration for a user. Encrypts sensitive config.
        Raises PluginServiceError or SupabaseClientError on failure.
        """
        try:
            encrypted_blob = KeyService.encrypt_config(config.encrypted_config_blob, user_id)
            data = config.dict()
            data["user_id"] = user_id
            data["encrypted_config_blob"] = encrypted_blob
            supabase = get_supabase_client()
            res = supabase.table(PLUGIN_TABLE).insert(data).execute()
            if res.data:
                return res.data[0]
            logger.error(f"Supabase insert error: {res.error}")
            raise SupabaseClientError(res.error)
        except Exception as e:
            logger.error(f"Error creating plugin config: {e}")
            raise PluginServiceError("Failed to create plugin configuration")

    @staticmethod
    async def get_plugin_config(config_id: str, user_id: str) -> Optional[dict]:
        """
        Retrieve a plugin configuration for a user by ID.
        Returns None if not found. Raises PluginServiceError on failure.
        """
        try:
            supabase = get_supabase_client()
            res = supabase.table(PLUGIN_TABLE).select("*").eq("id", config_id).eq("user_id", user_id).single().execute()
            return res.data if res.data else None
        except Exception as e:
            logger.error(f"Error fetching plugin config: {e}")
            raise PluginServiceError("Failed to fetch plugin configuration")

    @staticmethod
    async def update_plugin_config(config_id: str, user_id: str, config: PluginConfigurationUpdate) -> Optional[dict]:
        """
        Update a plugin configuration for a user. Encrypts sensitive config.
        Returns updated config or None. Raises PluginServiceError on failure.
        """
        try:
            encrypted_blob = KeyService.encrypt_config(config.encrypted_config_blob, user_id)
            data = config.dict()
            data["encrypted_config_blob"] = encrypted_blob
            supabase = get_supabase_client()
            res = supabase.table(PLUGIN_TABLE).update(data).eq("id", config_id).eq("user_id", user_id).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"Error updating plugin config: {e}")
            raise PluginServiceError("Failed to update plugin configuration")

    @staticmethod
    async def delete_plugin_config(config_id: str, user_id: str) -> bool:
        """
        Delete a plugin configuration for a user. Returns True if deleted.
        Raises PluginServiceError on failure.
        """
        try:
            supabase = get_supabase_client()
            res = supabase.table(PLUGIN_TABLE).delete().eq("id", config_id).eq("user_id", user_id).execute()
            return bool(res.data)
        except Exception as e:
            logger.error(f"Error deleting plugin config: {e}")
            raise PluginServiceError("Failed to delete plugin configuration")

    @staticmethod
    async def list_plugin_configs(user_id: str) -> list[dict]:
        """
        List all plugin configurations for a user.
        Raises PluginServiceError on failure.
        """
        try:
            supabase = get_supabase_client()
            res = supabase.table(PLUGIN_TABLE).select("*").eq("user_id", user_id).execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Error listing plugin configs: {e}")
            raise PluginServiceError("Failed to list plugin configurations")

    @staticmethod
    async def execute(config_id: str, inputs: dict) -> dict:
        """
        Execute a plugin using its configuration. Decrypts config and runs logic.
        Raises PluginServiceError on failure.
        """
        try:
            # Fetch config, decrypt, and execute plugin logic
            config = await PluginService.get_plugin_config(config_id, inputs.get("user_id"))
            if not config:
                logger.error(f"Plugin configuration not found: {config_id}")
                raise PluginServiceError("Plugin configuration not found")
            decrypted_config = KeyService.decrypt_config(config["encrypted_config_blob"], config["user_id"])
            plugin_type = config.get("plugin_type")
            # Plugin execution logic by type
            if plugin_type == "web_search":
                from app.plugins.web_search import run_web_search
                result = await run_web_search(inputs["query"], decrypted_config)
            elif plugin_type == "vectordb":
                from app.plugins.vectordb import run_vectordb_query
                result = await run_vectordb_query(inputs["query"], decrypted_config)
            else:
                result = {"message": "Plugin executed (stub)", "inputs": inputs, "config": decrypted_config}
            return {"result": result, "plugin_type": plugin_type}
        except Exception as e:
            logger.error(f"Error executing plugin: {e}")
            raise PluginServiceError("Failed to execute plugin")

# TODO: Refactor KeyService for async/await and Vault integration when ready.
# TODO: Add more granular plugin error types if needed.
