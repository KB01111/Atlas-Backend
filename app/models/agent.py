from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    color_theme: Optional[str] = None
    tags: Optional[List[str]] = []
    provider: Optional[str] = None
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    config: Optional[Any] = None
    plugin_config: Optional[Any] = None
    archived: Optional[bool] = False
    config_path: Optional[str] = None
    status: Optional[str] = None

    # Extensibility fields
    agent_type: Optional[str] = None
    graph_id: Optional[str] = None
    memory_config: Optional[Any] = None
    a2a_config: Optional[Any] = None
    plugin_config_id: Optional[str] = None
    output_schema: Optional[Any] = None

class AgentCreate(AgentBase):
    pass

class AgentUpdate(AgentBase):
    pass

class AgentOut(AgentBase):
    id: str
    user_id: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True