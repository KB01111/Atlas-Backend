from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

from app.core.security import get_current_user_id
from app.main import app

with patch("app.db.supabase_client.get_supabase_client") as mock_supabase_client:
    mock_supabase = MagicMock()
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    mock_table.insert.return_value.execute.return_value = MagicMock(
        data=[{"id": "test-agent", "user_id": "test-user"}], error=None
    )
    mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(
        data=[{"id": "test-agent", "user_id": "test-user"}], error=None
    )
    mock_table.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(
        data={"id": "test-agent", "user_id": "test-user"}, error=None
    )
    mock_table.update.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(
        data=[{"id": "test-agent", "user_id": "test-user"}], error=None
    )
    mock_table.delete.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(
        data=[{"id": "test-agent", "user_id": "test-user"}], error=None
    )
    mock_supabase_client.return_value = mock_supabase


@pytest.mark.asyncio
async def test_agent_crud(monkeypatch):
    # Mock authentication dependency to always return a test user_id
    app.dependency_overrides = {}
    app.dependency_overrides[get_current_user_id] = lambda: "test-user"

    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create agent
        agent_data = {"name": "Test Agent", "description": "Test", "config": {}}
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
