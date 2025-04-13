from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
import enum

class AgentFramework(str, enum.Enum):
    OPENAI_ASSISTANT = "OPENAI_ASSISTANT"
    GOOGLE_A2A = "GOOGLE_A2A"
    LITELLM_RAW = "LITELLM_RAW"
    CUSTOM = "CUSTOM"

class AgentBase(BaseModel):
    user_id: str
    name: str
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    framework: AgentFramework
    model: Optional[str] = None
    config: Optional[Any] = None
    plugin_config: Optional[Any] = None
    avatar_url: Optional[str] = None
    color_theme: Optional[str] = None
    tags: Optional[List[str]] = []
    config_path: Optional[str] = None

class AgentCreate(AgentBase):
    pass

class AgentUpdate(AgentBase):
    archived: Optional[bool] = None

class AgentOut(AgentBase):
    id: str
    archived: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True