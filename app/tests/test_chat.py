import pytest
from httpx import AsyncClient
from fastapi import status
from app.main import app

@pytest.mark.asyncio
async def test_chat_session_and_messages(monkeypatch):
    app.dependency_overrides = {
        "app.core.security.get_current_user_id": lambda: "test-user"
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create chat session
        session_data = {
            "name": "Test Session",
            "agent_id": "test-agent"
        }
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