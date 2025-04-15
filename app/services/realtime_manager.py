import asyncio
from typing import Any, Callable, Dict, List

from loguru import logger


class RealtimeManager:
    """
    Manages real-time event subscriptions and broadcasts for backend (Supabase Realtime or WebSocket).
    """
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[Any], None]]] = {}

    def subscribe(self, event: str, callback: Callable[[Any], None]):
        if event not in self.subscribers:
            self.subscribers[event] = []
        self.subscribers[event].append(callback)
        logger.info(f"Subscribed to event '{event}'")

    async def broadcast(self, event: str, payload: Any):
        for callback in self.subscribers.get(event, []):
            try:
                result = callback(payload)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Error in realtime subscriber for '{event}': {e}")

# Singleton instance for app-wide usage
realtime_manager = RealtimeManager()
