from unittest.mock import MagicMock, patch

with patch("app.db.supabase_client.get_supabase_client") as mock_supabase_client:
    mock_supabase = MagicMock()
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    # Mock insert for session creation
    mock_table.insert.return_value.execute.return_value = MagicMock(
        data=[
            {
                "id": "test-session",
                "name": "Test Session",
                "agent_id": "test-agent",
                "user_id": "test-user",
            }
        ],
        error=None,
    )
    # Mock select for list_sessions
    mock_table.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value = MagicMock(
        data=[
            {
                "id": "test-session",
                "name": "Test Session",
                "agent_id": "test-agent",
                "user_id": "test-user",
            }
        ],
        error=None,
    )
    # Mock select for get_messages
    mock_table.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = MagicMock(
        data=[], error=None
    )
    mock_supabase_client.return_value = mock_supabase

import pytest
from fastapi import status
from httpx import AsyncClient

from app.core.security import get_current_user_id
from app.main import app  # Standardized import

@pytest.mark.asyncio
async def test_chat_session_and_messages(monkeypatch):
    app.dependency_overrides = {}
    app.dependency_overrides[get_current_user_id] = lambda: "test-user"

    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create chat session
        session_data = {"name": "Test Session", "agent_id": "test-agent"}
        resp = await ac.post("/api/v1/chat/sessions", json=session_data)
        assert resp.status_code == status.HTTP_201_CREATED
        session = resp.json()
        session_id = session["id"]

        # List sessions
        resp = await ac.get("/api/v1/chat/sessions")
        assert resp.status_code == status.HTTP_200_OK
        assert any(s["id"] == session_id for s in resp.json())

        # Get messages (should be empty)
        resp = await ac.get(f"/api/v1/chat/sessions/{session_id}/messages")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == []
