from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from loguru import logger

from app.db.supabase_client import SupabaseClientError
from app.models.plugin import (
    PluginConfigurationCreate,
    PluginConfigurationOut,
    PluginConfigurationUpdate,
)
from app.services.plugin_service import PluginService, PluginServiceError


# Placeholder for user dependency (replace with real auth/user extraction)
def get_current_user():
    # TODO: Replace with actual authentication/authorization logic
    # Should return a user object or dict with at least 'id'
    return {"id": "test-user-id"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(prefix="/api/v1/plugins", tags=["plugins"])

@router.post("/", response_model=PluginConfigurationOut, status_code=status.HTTP_201_CREATED)
async def create_plugin_config(
    config: PluginConfigurationCreate,
    user = Depends(get_current_user)
):
    try:
        created = await PluginService.create_plugin_config(user["id"], config)
        return created
    except (PluginServiceError, SupabaseClientError) as e:
        logger.error(f"Plugin config creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[PluginConfigurationOut])
async def list_plugin_configs(user = Depends(get_current_user)):
    try:
        return await PluginService.list_plugin_configs(user["id"])
    except (PluginServiceError, SupabaseClientError) as e:
        logger.error(f"Plugin config listing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{config_id}", response_model=PluginConfigurationOut)
async def get_plugin_config(config_id: str, user = Depends(get_current_user)):
    try:
        config = await PluginService.get_plugin_config(config_id, user["id"])
        if not config:
            raise HTTPException(status_code=404, detail="Plugin configuration not found")
        return config
    except (PluginServiceError, SupabaseClientError) as e:
        logger.error(f"Plugin config fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{config_id}", response_model=PluginConfigurationOut)
async def update_plugin_config(
    config_id: str,
    config: PluginConfigurationUpdate,
    user = Depends(get_current_user)
):
    try:
        updated = await PluginService.update_plugin_config(config_id, user["id"], config)
        if not updated:
            raise HTTPException(status_code=404, detail="Plugin configuration not found")
        return updated
    except (PluginServiceError, SupabaseClientError) as e:
        logger.error(f"Plugin config update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plugin_config(config_id: str, user = Depends(get_current_user)):
    try:
        deleted = await PluginService.delete_plugin_config(config_id, user["id"])
        if not deleted:
            raise HTTPException(status_code=404, detail="Plugin configuration not found")
        return None
    except (PluginServiceError, SupabaseClientError) as e:
        logger.error(f"Plugin config deletion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{config_id}/execute", status_code=200)
async def execute_plugin_config(config_id: str, inputs: dict, user = Depends(get_current_user)):
    """
    Execute a plugin with the given config and user-provided inputs.
    """
    try:
        # Attach user_id to inputs for service logic
        inputs = dict(inputs or {})
        inputs["user_id"] = user["id"]
        result = await PluginService.execute(config_id, inputs)
        return result
    except (PluginServiceError, SupabaseClientError) as e:
        logger.error(f"Plugin execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
