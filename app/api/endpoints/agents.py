from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user_id as _get_current_user_id
from app.db.crud.crud_agent import (
    archive_agent,
    create_agent,
    get_agent_by_id,
    get_agents_by_user,
    update_agent,
)
from app.models.agent import AgentCreate, AgentOut, AgentUpdate

router = APIRouter(prefix="/agents", tags=["agents"])

get_current_user_id = Depends(_get_current_user_id)


@router.post("/", response_model=AgentOut, status_code=status.HTTP_201_CREATED)
async def create_agent_endpoint(agent: AgentCreate, user_id: str = get_current_user_id):
    """Create a new agent for the current user."""
    db_agent = await create_agent(user_id, agent)
    return db_agent


@router.get("/", response_model=list[AgentOut])
async def list_agents_endpoint(user_id: str = get_current_user_id):
    """List all agents for the current user."""
    agents = await get_agents_by_user(user_id)
    return agents


@router.get("/{agent_id}", response_model=AgentOut)
async def get_agent_endpoint(agent_id: str, user_id: str = get_current_user_id):
    """Retrieve a specific agent by ID for the current user."""
    agent = await get_agent_by_id(agent_id, user_id)
    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )
    return agent


@router.put("/{agent_id}", response_model=AgentOut)
async def update_agent_endpoint(
    agent_id: str, agent_update: AgentUpdate, user_id: str = get_current_user_id
):
    """Update an agent by ID for the current user."""
    updated = await update_agent(agent_id, user_id, agent_update)
    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Agent not found or not owned by user",
        )
    return updated


@router.delete("/{agent_id}", response_model=AgentOut)
async def archive_agent_endpoint(agent_id: str, user_id: str = get_current_user_id):
    """Archive (delete) an agent by ID for the current user."""
    archived = await archive_agent(agent_id, user_id)
    if not archived:
        raise HTTPException(
            status_code=404,
            detail="Agent not found or not owned by user",
        )
    return archived
