from app.db.supabase_client import supabase
from app.models.agent import AgentCreate, AgentUpdate
from typing import List, Optional

AGENT_TABLE = "agents"

async def create_agent(user_id: str, agent: AgentCreate) -> dict:
    data = agent.dict()
    data["user_id"] = user_id
    res = supabase.table(AGENT_TABLE).insert(data).execute()
    if res.data:
        return res.data[0]
    raise Exception(res.error)

async def get_agent_by_id(agent_id: str, user_id: str) -> Optional[dict]:
    res = supabase.table(AGENT_TABLE).select("*").eq("id", agent_id).eq("user_id", user_id).single().execute()
    if res.data:
        return res.data
    return None

async def get_agents_by_user(user_id: str) -> List[dict]:
    res = supabase.table(AGENT_TABLE).select("*").eq("user_id", user_id).eq("archived", False).execute()
    return res.data or []

async def update_agent(agent_id: str, user_id: str, agent: AgentUpdate) -> Optional[dict]:
    data = agent.dict(exclude_unset=True)
    res = supabase.table(AGENT_TABLE).update(data).eq("id", agent_id).eq("user_id", user_id).execute()
    if res.data:
        return res.data[0]
    return None

async def archive_agent(agent_id: str, user_id: str) -> Optional[dict]:
    res = supabase.table(AGENT_TABLE).update({"archived": True}).eq("id", agent_id).eq("user_id", user_id).execute()
    if res.data:
        return res.data[0]
    return None