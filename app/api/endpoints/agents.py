from fastapi import APIRouter, Depends, HTTPException, status
from app.models.agent import AgentCreate, AgentUpdate, AgentOut
from app.db.crud.crud_agent import (
    create_agent,
    get_agent_by_id,
    get_agents_by_user,
    update_agent,
    archive_agent,
)
from app.core.security import get_current_user_id
from typing import List

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("/", response_model=AgentOut, status_code=status.HTTP_201_CREATED)
async def create_agent_endpoint(
    agent: AgentCreate,
    user_id: str = Depends(get_current_user_id)
):
    db_agent = await create_agent(user_id, agent)
    return db_agent

@router.get("/", response_model=List[AgentOut])
async def list_agents_endpoint(
    user_id: str = Depends(get_current_user_id)
):
    agents = await get_agents_by_user(user_id)
    return agents

@router.get("/{agent_id}", response_model=AgentOut)
async def get_agent_endpoint(
    agent_id: str,
    user_id: str = Depends(get_current_user_id)
):
    agent = await get_agent_by_id(agent_id, user_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.put("/{agent_id}", response_model=AgentOut)
async def update_agent_endpoint(
    agent_id: str,
    agent_update: AgentUpdate,
    user_id: str = Depends(get_current_user_id)
):
    updated = await update_agent(agent_id, user_id, agent_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Agent not found or not owned by user")
    return updated

@router.delete("/{agent_id}", response_model=AgentOut)
async def archive_agent_endpoint(
    agent_id: str,
    user_id: str = Depends(get_current_user_id)
):
    archived = await archive_agent(agent_id, user_id)
    if not archived:
        raise HTTPException(status_code=404, detail="Agent not found or not owned by user")
    return archived