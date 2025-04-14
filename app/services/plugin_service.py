from app.db.supabase_client import supabase
from app.models.plugin import (
    PluginConfigurationCreate,
    PluginConfigurationUpdate,
)
from app.services.key_service import KeyService
from typing import Optional

PLUGIN_TABLE = "plugin_configurations"

class PluginService:
    @staticmethod
    async def create_plugin_config(user_id: str, config: PluginConfigurationCreate) -> dict:
        # Encrypt sensitive config using KeyService (placeholder)
        encrypted_blob = KeyService.encrypt_config(config.encrypted_config_blob, user_id)
        data = config.dict()
        data["user_id"] = user_id
        data["encrypted_config_blob"] = encrypted_blob
        res = supabase.table(PLUGIN_TABLE).insert(data).execute()
        if res.data:
            return res.data[0]
        raise PluginServiceError(res.error)

    @staticmethod
    async def get_plugin_config(config_id: str, user_id: str) -> Optional[dict]:
        res = supabase.table(PLUGIN_TABLE).select("*").eq("id", config_id).eq("user_id", user_id).single().execute()
        return res.data if res.data else None

    @staticmethod
    async def update_plugin_config(config_id: str, user_id: str, config: PluginConfigurationUpdate) -> Optional[dict]:
        encrypted_blob = KeyService.encrypt_config(config.encrypted_config_blob, user_id)
        data = config.dict()
        data["encrypted_config_blob"] = encrypted_blob
        res = supabase.table(PLUGIN_TABLE).update(data).eq("id", config_id).eq("user_id", user_id).execute()
        return res.data[0] if res.data else None

    @staticmethod
    async def delete_plugin_config(config_id: str, user_id: str) -> bool:
        res = supabase.table(PLUGIN_TABLE).delete().eq("id", config_id).eq("user_id", user_id).execute()
        return bool(res.data)

    @staticmethod
    async def list_plugin_configs(user_id: str) -> list[dict]:
        res = supabase.table(PLUGIN_TABLE).select("*").eq("user_id", user_id).execute()
        return res.data or []

    @staticmethod
    async def execute(config_id: str, inputs: dict) -> dict:
        # Placeholder for plugin execution logic
        # Fetch config, decrypt, and execute plugin logic
        config = await PluginService.get_plugin_config(config_id, inputs.get("user_id"))
        if not config:
            # Define or import PluginConfigurationNotFoundError before using it.
            raise Exception("Plugin configuration not found")
        # Decrypt config (placeholder)
        decrypted_config = KeyService.decrypt_config(config["encrypted_config_blob"], config["user_id"])
        # Plugin execution logic goes here
        return {"result": "Plugin executed (stub)", "config": decrypted_config, "inputs": inputs}