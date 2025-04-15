from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, field_validator


class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    color_theme: Optional[str] = None
    tags: Optional[List[str]] = None
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
    memory_config: Optional[dict] = None  # Example: Configuration for memory management
    a2a_config: Optional[dict] = (
        None  # Example: Configuration for agent-to-agent communication
    )
    plugin_config_id: Optional[str] = None
    output_schema: Optional[dict] = None  # Example: Schema for the agent's output

    @field_validator("tags", mode="before")
    @classmethod
    def default_tags(cls, v):
        return v or []


class AgentCreate(AgentBase):
    pass


class AgentUpdate(AgentBase):
    pass


class AgentOut(AgentBase):
    id: str
    user_id: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)
