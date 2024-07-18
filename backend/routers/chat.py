import json

from database import SessionLocal, get_db
from fastapi import (
    APIRouter,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
)
from routers.user import get_current_user, user_picture_B64
from websockets.frames import CloseCode

router = APIRouter(prefix="/chat", tags=["chat"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def send_room_data(self, websocket: WebSocket):
        await websocket.send_json(["roomData", {"users": len(self.active_connections)}])

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        token = await websocket.receive_text()

        try:
            async with SessionLocal() as db:
                try:
                    user = await get_current_user(token, db)
                except HTTPException:
                    await websocket.close(
                        CloseCode.INTERNAL_ERROR, "authentication failed"
                    )
                    await db.close()
                    return None
        finally:
            await db.close()

        avatar, username = user_picture_B64(user.picture), user.username

        con = self.active_connections.get(username)
        if con is not None:
            await con.send_json(
                ["disconnected", {"details": "Logged in from elsewhere"}]
            )
            await con.close(CloseCode.INTERNAL_ERROR, "logged in from elsewhere")
        self.active_connections[username] = websocket

        await self.broadcast(
            json.dumps(["joinRoom", {"username": username, "avatar": avatar}])
        )
        await self.send_room_data(websocket)
        return avatar, username

    def disconnect(self, username: str, websocket):
        ws = self.active_connections.get(username)
        if ws is None:
            return
        elif ws == websocket:
            del self.active_connections[username]

    async def send_personal_message(self, username: str, message: str):
        ws = self.active_connections.get(username)
        if ws is None:
            raise WebSocketException(
                404, f"Connection with username {username} not found"
            )
        await ws.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

    async def broadcast_room_data(self):
        await self.broadcast(
            json.dumps(["roomData", {"users": len(self.active_connections)}])
        )


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    resp = await manager.connect(websocket)
    if resp is None:
        return
    avatar, username = resp
    try:
        while True:
            data = await websocket.receive_json()
            data[1]["avatar"] = avatar
            data[1]["username"] = username
            await manager.broadcast(json.dumps(data))
    except WebSocketDisconnect:
        manager.disconnect(username, websocket)
        await manager.broadcast(
            json.dumps(["leaveRoom", {"username": username, "avatar": avatar}])
        )
