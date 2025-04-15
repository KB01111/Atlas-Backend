from __future__ import annotations

"""
A2A Service: Implements Google Agent2Agent (A2A) protocol logic for agent registration, handshake, message relay, status, and error handling.
All references to 'a2a' refer exclusively to the Google A2A protocol.
See: https://google.github.io/A2A/#/documentation
"""

from typing import Optional

import httpx
from loguru import logger

from app.models.a2a import (
    A2AErrorResponse,
    A2AHandshakeRequest,
    A2AHandshakeResponse,
    A2ARegistrationRequest,
    A2ARegistrationResponse,
    A2ARequest,
    A2AResponse,
    A2AStatusResponse,
)
from app.services.key_service import get_api_key


class A2AService:
    """Implements Google A2A protocol operations: registration, handshake, relay, status, error."""

    @staticmethod
    async def register_agent(
        payload: A2ARegistrationRequest,
    ) -> A2ARegistrationResponse:
        """Register this agent with the A2A registry or another agent."""
        # TODO: Implement registration logic (DB, registry, etc.)
        return A2ARegistrationResponse(success=True, agent_id="agent-123")

    @staticmethod
    async def handshake(payload: A2AHandshakeRequest) -> A2AHandshakeResponse:
        """Perform handshake/authentication with another agent."""
        # TODO: Implement handshake/auth logic (token validation, session setup)
        return A2AHandshakeResponse(success=True, session_token="session-abc")

    @staticmethod
    async def send_a2a(payload: A2ARequest, user_id: str) -> A2AResponse:
        """Relay an A2A message to another agent using the Google A2A protocol."""
        try:
            api_key = await get_api_key(user_id, "a2a")
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            request_payload = {
                "jsonrpc": "2.0",
                "method": payload.method,
                "params": payload.params,
                "id": "1",
            }
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{payload.to_agent_url.rstrip('/')}/tasks/send",
                    json=request_payload,
                    headers=headers,
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
            agent_card = await A2AService.fetch_agent_card(payload.to_agent_url)
            return A2AResponse(
                result=data.get("result"),
                error=data.get("error"),
                agent_card=agent_card,
            )
        except httpx.HTTPStatusError as exc:
            logger.error(
                f"A2A send HTTP error: {exc.response.status_code} {exc.response.text}"
            )
            return A2AResponse(
                result=None,
                error=f"HTTP error {exc.response.status_code}: {exc.response.text}",
            )
        except httpx.RequestError as exc:
            logger.error(f"A2A send request error: {exc}")
            return A2AResponse(result=None, error=str(exc))
        except Exception as exc:
            logger.error(f"A2A send unexpected error: {exc}")
            return A2AResponse(result=None, error=str(exc))

    @staticmethod
    async def receive_a2a(payload: A2ARequest, user_id: str) -> A2AResponse:
        """Receive/process an incoming A2A message (Google A2A protocol)."""
        # TODO: Implement full protocol logic: validation, acknowledgment, error handling
        return A2AResponse(result="A2A task received", error=None)

    @staticmethod
    async def fetch_agent_card(agent_url: str) -> dict:
        """Fetch the agent's metadata card from the well-known endpoint."""
        url = f"{agent_url.rstrip('/')}/.well-known/agent.json"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
            resp.raise_for_status()
            return resp.json()

    @staticmethod
    async def status(agent_id: str) -> A2AStatusResponse:
        """Return the current status of this agent (Google A2A protocol)."""
        # TODO: Implement agent status logic
        return A2AStatusResponse(status="online", message="Agent is healthy.")

    @staticmethod
    async def error_response(
        error: str, code: Optional[int] = None, details: Optional[dict] = None
    ) -> A2AErrorResponse:
        """Return a Google A2A protocol error response."""
        return A2AErrorResponse(error=error, code=code, details=details)
