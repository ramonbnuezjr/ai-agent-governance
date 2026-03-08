"""WebSocket: subscribe by session_id, receive live events and evaluations."""

import asyncio
import json
import logging
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

# session_id -> set of WebSocket
_subscribers: dict[str, set[WebSocket]] = {}
_lock = asyncio.Lock()
# Main event loop (set at app startup) for thread-safe broadcast
_loop: asyncio.AbstractEventLoop | None = None


def set_event_loop(loop: asyncio.AbstractEventLoop) -> None:
    global _loop
    _loop = loop


def get_loop() -> asyncio.AbstractEventLoop | None:
    return _loop


async def subscribe(session_id: str, ws: WebSocket) -> None:
    """Add connection to session's subscriber set."""
    await ws.accept()
    async with _lock:
        _subscribers.setdefault(session_id, set()).add(ws)


async def unsubscribe(session_id: str, ws: WebSocket) -> None:
    """Remove connection."""
    async with _lock:
        s = _subscribers.get(session_id)
        if s:
            s.discard(ws)
            if not s:
                del _subscribers[session_id]


async def broadcast(session_id: str, kind: str, payload: dict[str, Any]) -> None:
    """Send a message to all subscribers of this session."""
    msg = json.dumps({"kind": kind, "payload": payload})
    async with _lock:
        subs = list(_subscribers.get(session_id, set()))
    for ws in subs:
        try:
            await ws.send_text(msg)
        except Exception as e:
            logger.debug("WS send failed: %s", e)


async def broadcast_event(session_id: str, event: dict[str, Any]) -> None:
    """Broadcast an ATS event."""
    await broadcast(session_id, "event", event)


async def broadcast_evaluation(session_id: str, evaluation: dict[str, Any]) -> None:
    """Broadcast a policy evaluation."""
    await broadcast(session_id, "evaluation", evaluation)


def broadcast_event_sync(session_id: str, event: dict[str, Any]) -> None:
    """Thread-safe: schedule broadcast from runner thread."""
    loop = get_loop()
    if loop and not loop.is_closed():
        asyncio.run_coroutine_threadsafe(broadcast_event(session_id, event), loop)


def broadcast_evaluation_sync(session_id: str, evaluation: dict[str, Any]) -> None:
    """Thread-safe: schedule broadcast from runner thread."""
    loop = get_loop()
    if loop and not loop.is_closed():
        asyncio.run_coroutine_threadsafe(broadcast_evaluation(session_id, evaluation), loop)
