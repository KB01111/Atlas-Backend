import pytest
from httpx import AsyncClient

from app.core.security import get_current_user_id
from app.main import app


@pytest.mark.asyncio
async def test_a2a_register_agent(async_client: AsyncClient):
    app.dependency_overrides[get_current_user_id] = lambda: "test-user"
    payload = {
        "agent_url": "http://localhost:8000/api/v1/a2a",
        "agent_name": "TestAgent",
        "capabilities": {"echo": True},
    }
    response = await async_client.post("/api/v1/a2a/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "agent_id" in data

@pytest.mark.asyncio
async def test_a2a_handshake(async_client: AsyncClient):
    payload = {"agent_id": "agent-123", "token": "secret-token"}
    response = await async_client.post("/api/v1/a2a/handshake", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "session_token" in data

@pytest.mark.asyncio
async def test_a2a_send_and_receive(async_client: AsyncClient):
    app.dependency_overrides[get_current_user_id] = lambda: "test-user"
    payload = {
        "to_agent_url": "http://localhost:8000/api/v1/a2a",
        "method": "echo",
        "params": {"msg": "hello"},
    }
    # Send
    response = await async_client.post("/api/v1/a2a/send", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "result" in data or "error" in data
    # Receive
    response = await async_client.post("/api/v1/a2a/receive", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "A2A task received"

@pytest.mark.asyncio
async def test_a2a_status(async_client: AsyncClient):
    response = await async_client.get("/api/v1/a2a/status/agent-123")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"

@pytest.mark.asyncio
async def test_a2a_error(async_client: AsyncClient):
    response = await async_client.get("/api/v1/a2a/error", params={"error": "fail", "code": 400})
    assert response.status_code == 200
    data = response.json()
    assert data["error"] == "fail"
    assert data["code"] == 400
