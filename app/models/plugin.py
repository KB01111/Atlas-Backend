from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

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

    class Config:
        orm_mode = True