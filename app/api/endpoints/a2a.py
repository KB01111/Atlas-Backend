"""API Endpoints for Google Agent-to-Agent (A2A) Communication Protocol.

Implements registration, handshake, and message relay according to the A2A spec.
Ref: https://google.github.io/A2A/#/documentation
"""

import logging
from typing import Annotated, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status

from app.core.security import get_current_user_id
from app.models.a2a import (
    A2AErrorResponse,
    A2AHandshakeRequest,
    A2AHandshakeResponse,
    A2AMessage,
    A2ARegistrationRequest,
    A2ARegistrationResponse,
    A2ARequest,
    A2AResponse,
    A2AStatusResponse,
)
from app.services.a2a_service import A2AService

logger = logging.getLogger(__name__)


def get_a2a_service():
    """FastAPI dependency injector for A2AService."""
    return A2AService()


router = APIRouter(prefix="/api/v1/a2a", tags=["a2a"])


@router.post("/register", response_model=A2ARegistrationResponse)
async def register_agent(
    request: A2ARegistrationRequest,
    a2a_service: Annotated[A2AService, Depends(get_a2a_service)],
    # current_user: Annotated[User, Depends(get_current_active_user)] # TODO: Add auth
) -> A2ARegistrationResponse:
    """Register an agent instance with the A2A service.

    Allows an agent to announce its presence and capabilities.
    """
    logger.info(f"Received A2A registration request for agent: {request.agent_id}")
    try:
        response = await a2a_service.handle_registration(request)
        logger.info(f"Agent {request.agent_id} registered successfully.")
        return response
    except Exception as e:
        logger.exception(f"Error during A2A registration for agent {request.agent_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {e}",
        ) from e


@router.post("/handshake", response_model=A2AHandshakeResponse)
async def perform_handshake(
    request: A2AHandshakeRequest,
    a2a_service: Annotated[A2AService, Depends(get_a2a_service)],
    # current_user: Annotated[User, Depends(get_current_active_user)] # TODO: Add auth
) -> A2AHandshakeResponse:
    """Initiate or respond to an A2A handshake between agents.

    Establishes secure communication channels.
    """
    logger.info(
        f"Received A2A handshake request from {request.sender_id} "
        f"to {request.receiver_id}"
    )
    try:
        response = await a2a_service.handle_handshake(request)
        logger.info(
            f"A2A handshake successful between {request.sender_id} "
            f"and {request.receiver_id}"
        )
        return response
    except ValueError as ve:
        logger.warning(f"A2A handshake validation error: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Handshake error: {ve}"
        ) from ve
    except Exception as e:
        logger.exception(
            f"Error during A2A handshake between {request.sender_id} "
            f"and {request.receiver_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Handshake failed: {e}",
        ) from e


@router.post("/message", status_code=status.HTTP_202_ACCEPTED)
async def relay_message(
    request: A2AMessage,
    a2a_service: Annotated[A2AService, Depends(get_a2a_service)],
    background_tasks: BackgroundTasks,
    # current_user: Annotated[User, Depends(get_current_active_user)] # TODO: Add auth
) -> dict[str, str]:
    """Receive and relay an A2A message to the intended recipient agent.

    Uses background tasks for asynchronous delivery.
    """
    logger.info(
        f"Received A2A message relay request from {request.sender_id} "
        f"to {request.receiver_id}"
    )
    try:
        # Validate message structure before queueing
        # Minimal validation here; deeper validation in the service
        if not request.sender_id or not request.receiver_id or not request.payload:
            raise ValueError("Invalid A2A message structure")

        background_tasks.add_task(a2a_service.handle_message_relay, request)
        logger.info(
            f"A2A message from {request.sender_id} to {request.receiver_id} "
            f"queued for relay."
        )
        return {"status": "Message relay accepted"}
    except ValueError as ve:
        logger.warning(f"A2A message relay validation error: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Message relay error: {ve}"
        ) from ve
    except Exception as e:
        logger.exception(
            f"Error queueing A2A message relay from {request.sender_id} "
            f"to {request.receiver_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Message relay failed: {e}",
        ) from e


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


@router.post("/error", response_model=A2AErrorResponse)
async def error_response(error: str, code: Optional[int] = None):
    """Google A2A: Return a protocol-compliant error response."""
    try:
        return await A2AService.error_response(error, code)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
