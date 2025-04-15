from __future__ import annotations

"""
A2A Endpoints: All endpoints in this file implement the Google Agent2Agent (A2A) protocol.
Any reference to 'a2a' refers exclusively to Google A2A: https://google.github.io/A2A/#/documentation
"""

from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.security import get_current_user_id
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
from app.services.a2a_service import A2AService

router = APIRouter(prefix="/api/v1/a2a", tags=["a2a"])

@router.post("/register", response_model=A2ARegistrationResponse)
async def register_agent(payload: A2ARegistrationRequest):
    """Google A2A: Register this agent with the registry or another agent."""
    try:
        return await A2AService.register_agent(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.post("/handshake", response_model=A2AHandshakeResponse)
async def handshake(payload: A2AHandshakeRequest):
    """Google A2A: Perform handshake/authentication with another agent."""
    try:
        return await A2AService.handshake(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.post("/send", response_model=A2AResponse)
async def send_a2a(
    request: Request,
    payload: A2ARequest,
    user_id: str = Depends(get_current_user_id),
):
    """Google A2A: Relay a message to another agent."""
    try:
        result = await A2AService.send_a2a(payload, user_id)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.post("/receive", response_model=A2AResponse)
async def receive_a2a(
    request: Request,
    payload: A2ARequest,
    user_id: str = Depends(get_current_user_id),
):
    """Google A2A: Receive/process an incoming message."""
    try:
        result = await A2AService.receive_a2a(payload, user_id)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.get("/status/{agent_id}", response_model=A2AStatusResponse)
async def agent_status(agent_id: str):
    """Google A2A: Get the current status of this agent."""
    try:
        return await A2AService.status(agent_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.get("/error", response_model=A2AErrorResponse)
async def error_response(error: str, code: int = None):
    """Google A2A: Return a protocol-compliant error response."""
    return await A2AService.error_response(error, code)
