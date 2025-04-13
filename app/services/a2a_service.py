import httpx
from app.services.key_service import get_api_key

async def fetch_agent_card(agent_url: str) -> dict:
    url = f"{agent_url.rstrip('/')}/.well-known/agent.json"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()

async def send_a2a_task(user_id: str, agent_url: str, method: str, params: dict, service: str = "a2a"):
    # Optionally retrieve an API key for A2A if needed
    api_key = await get_api_key(user_id, service)
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": "1"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{agent_url.rstrip('/')}/tasks/send", json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()