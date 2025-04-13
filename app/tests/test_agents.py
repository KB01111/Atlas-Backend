import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app

@pytest.mark.asyncio
async def test_agent_crud(monkeypatch):
    # Mock authentication dependency to always return a test user_id
    app.dependency_overrides = {}
    app.dependency_overrides = {
        "app.core.security.get_current_user_id": lambda: "test-user"
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create agent
        agent_data = {
            "name": "Test Agent",
            "description": "A test agent",
            "provider": "openai",
            "model": "gpt-4-turbo"
        }
        resp = await ac.post("/api/v1/agents/", json=agent_data)
        assert resp.status_code == status.HTTP_201_CREATED
        agent = resp.json()
        agent_id = agent["id"]

        # List agents
        resp = await ac.get("/api/v1/agents/")
        assert resp.status_code == status.HTTP_200_OK
        assert any(a["id"] == agent_id for a in resp.json())

        # Get agent by id
        resp = await ac.get(f"/api/v1/agents/{agent_id}")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["id"] == agent_id

        # Update agent
        update_data = {"description": "Updated"}
        resp = await ac.put(f"/api/v1/agents/{agent_id}", json=update_data)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["description"] == "Updated"

        # Archive agent
        resp = await ac.delete(f"/api/v1/agents/{agent_id}")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["archived"] is True