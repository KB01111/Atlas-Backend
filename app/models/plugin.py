from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PluginConfigurationBase(BaseModel):
    plugin_type: str
    name: str
    encrypted_config_blob: str


class PluginConfigurationCreate(PluginConfigurationBase):
    pass


class PluginConfigurationUpdate(PluginConfigurationBase):
    pass


class PluginConfigurationOut(PluginConfigurationBase):
    id: str
    user_id: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)
