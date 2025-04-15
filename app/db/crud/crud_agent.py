from typing import List, Optional

from loguru import logger

from app.db.supabase_client import SupabaseClientError, get_supabase_client
from app.models.agent import AgentCreate, AgentUpdate

AGENT_TABLE = "agents"

# Replace all usages of 'supabase' with the result of get_supabase_client() where needed.
# For example:
# supabase = get_supabase_client()

async def create_agent(user_id: str, agent: AgentCreate) -> dict:
    """
    Create a new agent for a user.
    Raises SupabaseClientError on failure.
    """
    data = agent.dict()
    data["user_id"] = user_id
    supabase = get_supabase_client()
    try:
        res = supabase.table(AGENT_TABLE).insert(data).execute()
        if res.data:
            return res.data[0]
        logger.error(f"Supabase insert error: {res.error}")
        raise SupabaseClientError(res.error)
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise SupabaseClientError("Failed to create agent")

async def get_agent_by_id(agent_id: str, user_id: str) -> Optional[dict]:
    """
    Retrieve an agent by ID and user.
    Returns None if not found.
    Raises SupabaseClientError on failure.
    """
    supabase = get_supabase_client()
    try:
        res = supabase.table(AGENT_TABLE).select("*").eq("id", agent_id).eq("user_id", user_id).single().execute()
        if res.data:
            return res.data
        return None
    except Exception as e:
        logger.error(f"Error fetching agent by id: {e}")
        raise SupabaseClientError("Failed to fetch agent")

async def get_agents_by_user(user_id: str) -> List[dict]:
    """
    Retrieve all non-archived agents for a user.
    Returns empty list if none found.
    Raises SupabaseClientError on failure.
    """
    supabase = get_supabase_client()
    try:
        res = supabase.table(AGENT_TABLE).select("*").eq("user_id", user_id).eq("archived", False).execute()
        return res.data or []
    except Exception as e:
        logger.error(f"Error fetching agents by user: {e}")
        raise SupabaseClientError("Failed to fetch agents")

async def update_agent(agent_id: str, user_id: str, agent: AgentUpdate) -> Optional[dict]:
    """
    Update an agent for a user.
    Returns updated agent dict or None.
    Raises SupabaseClientError on failure.
    """
    data = agent.dict(exclude_unset=True)
    supabase = get_supabase_client()
    try:
        res = supabase.table(AGENT_TABLE).update(data).eq("id", agent_id).eq("user_id", user_id).execute()
        if res.data:
            return res.data[0]
        return None
    except Exception as e:
        logger.error(f"Error updating agent: {e}")
        raise SupabaseClientError("Failed to update agent")

async def archive_agent(agent_id: str, user_id: str) -> Optional[dict]:
    """
    Archive an agent for a user.
    Returns updated agent dict or None.
    Raises SupabaseClientError on failure.
    """
    supabase = get_supabase_client()
    try:
        res = supabase.table(AGENT_TABLE).update({"archived": True}).eq("id", agent_id).eq("user_id", user_id).execute()
        if res.data:
            return res.data[0]
        return None
    except Exception as e:
        logger.error(f"Error archiving agent: {e}")
        raise SupabaseClientError("Failed to archive agent")

# TODO: When async supabase client is available, refactor these methods to async and use await.
# TODO: Integrate KeyService for secure secret handling when available.
