from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user_id
from app.models.plugin import (
    PluginConfigurationCreate,
    PluginConfigurationOut,
    PluginConfigurationUpdate,
)
from app.services.plugin_service import PluginService

router = APIRouter()

@router.post("/", response_model=PluginConfigurationOut)
async def create_plugin_config(
    config: PluginConfigurationCreate,
    user_id: str = Depends(get_current_user_id)
):
    return await PluginService.create_plugin_config(user_id, config)

@router.get("/{config_id}", response_model=PluginConfigurationOut)
async def get_plugin_config(
    config_id: str,
    user_id: str = Depends(get_current_user_id)
):
    config = await PluginService.get_plugin_config(config_id, user_id)
    if not config:
        raise HTTPException(status_code=404, detail="Plugin configuration not found")
    return config

@router.put("/{config_id}", response_model=PluginConfigurationOut)
async def update_plugin_config(
    config_id: str,
    config: PluginConfigurationUpdate,
    user_id: str = Depends(get_current_user_id)
):
    updated = await PluginService.update_plugin_config(config_id, user_id, config)
    if not updated:
        raise HTTPException(status_code=404, detail="Plugin configuration not found")
    return updated

@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plugin_config(
    config_id: str,
    user_id: str = Depends(get_current_user_id)
):
    deleted = await PluginService.delete_plugin_config(config_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Plugin configuration not found")
    return

@router.get("/", response_model=List[PluginConfigurationOut])
async def list_plugin_configs(
    user_id: str = Depends(get_current_user_id)
):
    return await PluginService.list_plugin_configs(user_id)
