import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["alerts"])

# Connected WebSocket clients
connected_clients: set[WebSocket] = set()


@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """WebSocket endpoint for real-time doctor alerts."""
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            # Keep connection alive — client can also send pings
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.discard(websocket)


async def broadcast_alert(data: dict):
    """Broadcast an alert to all connected WebSocket clients."""
    if not connected_clients:
        return

    message = json.dumps(data)
    disconnected = set()

    for client in connected_clients:
        try:
            await client.send_text(message)
        except Exception:
            disconnected.add(client)

    connected_clients.difference_update(disconnected)
