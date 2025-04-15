from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class WorkflowStep(BaseModel):
    id: str
    type: str  # e.g., 'plugin', 'agent', 'tool', etc.
    config_id: Optional[str] = None  # Plugin or agent config reference
    parameters: Optional[Dict[str, Any]] = None


class WorkflowBase(BaseModel):
    name: str
    description: Optional[str] = None
    steps: List[WorkflowStep]


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[WorkflowStep]] = None


class WorkflowOut(WorkflowBase):
    id: str
    user_id: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


class WorkflowRunRequest(BaseModel):
    inputs: Dict[str, Any]


class WorkflowRunResult(BaseModel):
    status: str
    output: Any
    logs: Optional[List[str]] = None
