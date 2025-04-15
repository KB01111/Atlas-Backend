from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

"""
All models in this file implement the Google Agent2Agent (A2A) protocol.

Any reference to 'a2a' in this codebase refers exclusively to the Google A2A protocol:
https://google.github.io/A2A/#/documentation
"""

class A2AMessageEnvelope(BaseModel):
    """
    Google A2A protocol message envelope.
    """

    sender: str = Field(..., description="Sender agent URL or ID")
    receiver: str = Field(..., description="Receiver agent URL or ID")
    message_id: str = Field(..., description="Unique message ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp of the message")
    protocol_version: str = Field(default="1.0", description="A2A protocol version")
    method: str = Field(..., description="A2A method to call")
    params: dict[str, Any] = Field(default_factory=dict, description="Method parameters")
    metadata: Optional[dict[str, Any]] = Field(default=None, description="Optional metadata for extensibility")


class A2ARegistrationRequest(BaseModel):
    """
    Google A2A protocol agent registration request.
    """

    agent_url: str = Field(..., description="Agent's public endpoint URL")
    agent_name: str = Field(..., description="Human-readable agent name")
    capabilities: Optional[dict[str, Any]] = Field(default=None, description="Agent capabilities/features")


class A2ARegistrationResponse(BaseModel):
    """
    Google A2A protocol agent registration response.
    """

    success: bool
    error: Optional[str] = None
    agent_id: Optional[str] = None


class A2AHandshakeRequest(BaseModel):
    """
    Google A2A protocol handshake request.
    """

    agent_id: str
    token: str


class A2AHandshakeResponse(BaseModel):
    """
    Google A2A protocol handshake response.
    """

    success: bool
    session_token: Optional[str] = None
    error: Optional[str] = None


class A2AStatusResponse(BaseModel):
    """
    Google A2A protocol status response.
    """

    status: str
    message: Optional[str] = None


class A2AErrorResponse(BaseModel):
    """
    Google A2A protocol error response.
    """

    error: str
    code: Optional[int] = None
    details: Optional[dict[str, Any]] = None


# Legacy compatibility (deprecated, but kept for backward compatibility)
class A2ARequest(BaseModel):
    """
    Legacy A2A request model.
    """

    to_agent_url: str = Field(..., description="Target agent endpoint URL")
    method: str = Field(..., description="A2A method to call")
    params: dict[str, Any] = Field(default_factory=dict, description="Method parameters")


class A2AResponse(BaseModel):
    """
    Legacy A2A response model.
    """

    result: Optional[Any] = None
    error: Optional[str] = None
    agent_card: Optional[dict[str, Any]] = None
