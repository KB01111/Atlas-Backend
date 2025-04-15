import asyncio
from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.realtime_manager import realtime_manager

router = APIRouter()

active_connections: List[WebSocket] = []

@router.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_json()
            # Optionally, handle incoming events from client
    except WebSocketDisconnect:
        active_connections.remove(websocket)

# Broadcast helper for backend events
async def broadcast_event(event: str, payload):
    for ws in active_connections:
        try:
            await ws.send_json({"event": event, "payload": payload})
        except Exception:
            pass

# Register broadcast with the realtime manager
realtime_manager.subscribe(
    "broadcast",
    lambda payload: asyncio.create_task(broadcast_event(payload["event"], payload["payload"]))
)
