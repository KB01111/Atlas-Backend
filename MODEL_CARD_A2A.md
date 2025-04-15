# Model Card: Google A2A Protocol Support

## Overview
This backend implements the [Google Agent2Agent (A2A) protocol](https://google.github.io/A2A/#/documentation) for standardized, secure, and interoperable agent communication. All `/api/v1/a2a/` endpoints are compliant with the A2A protocol envelope, registration, handshake, message relay, status, and error response specifications.

## Supported Flows
- Agent Registration: `/api/v1/a2a/register`
- Handshake: `/api/v1/a2a/handshake`
- Message Send/Relay: `/api/v1/a2a/send`
- Message Receive: `/api/v1/a2a/receive`
- Status: `/api/v1/a2a/status/{agent_id}`
- Error: `/api/v1/a2a/error`

## Compliance
- Message envelopes, registration, handshake, and error models match [Google A2A schema](https://google.github.io/A2A/#/documentation).
- Async FastAPI endpoints, Pydantic v2 models, and robust error handling.
- Extensible for custom agent capabilities.

## Limitations
- This implementation is a reference and may require further extension for production, including full registry integration and advanced authentication.

## References
- [Google A2A Protocol Docs](https://google.github.io/A2A/#/documentation)
- See `app/models/a2a.py`, `app/services/a2a_service.py`, `app/api/endpoints/a2a.py`
