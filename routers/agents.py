from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..database import get_db
from ..models import Agent
from ..schemas import AgentCreate, AgentOut, AgentUpdate

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("/", response_model=AgentOut, status_code=status.HTTP_201_CREATED)
async def create_agent(agent: AgentCreate, db: AsyncSession = Depends(get_db)):
    db_agent = Agent(
        id=str(uuid4()),
        **agent.dict()
    )
    db.add(db_agent)
    await db.commit()
    await db.refresh(db_agent)
    return db_agent

@router.get("/", response_model=list[AgentOut])
async def list_agents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.archived is False))
    agents = result.scalars().all()
    return agents

@router.get("/{agent_id}", response_model=AgentOut)
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.put("/{agent_id}", response_model=AgentOut)
async def update_agent(agent_id: str, agent_update: AgentUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    for key, value in agent_update.dict(exclude_unset=True).items():
        setattr(agent, key, value)
    await db.commit()
    await db.refresh(agent)
    return agent

@router.delete("/{agent_id}", response_model=AgentOut)
async def archive_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent.archived = True
    await db.commit()
    await db.refresh(agent)
    return agent
