from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from routers.user import user_dependency

router = APIRouter(prefix="/chat", tags=["chat"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def send_room_data(self, websocket: WebSocket):
        await websocket.send_json(["roomData", {"users": len(self.active_connections)}])

    async def broadcast_room_data(self):
        for connection in self.active_connections:
            await connection.send_json(
                ["roomData", {"users": len(self.active_connections)}]
            )

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        await self.send_room_data(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect(websocket)
    await manager.broadcast_room_data()
    try:
        while True:
            data = await websocket.receive_text()
            # await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"{username} left the chat")
