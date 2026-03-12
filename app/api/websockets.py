from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        # Convert datetime objects if any, though we'll broadcast raw dicts/JSON strings
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass # Ignoring dropped connections silently

manager = ConnectionManager()

@router.websocket("/live-dashboard")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Client can send commands if needed, for instance, "ping"
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"message": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
