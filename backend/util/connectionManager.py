from typing import Any

from database import SessionLocal
from fastapi import HTTPException, WebSocket, WebSocketException
from models import Users
from routers.user import get_current_user
from websockets.frames import CloseCode


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def auth_user(self, ws: WebSocket) -> Users | None:
        await ws.send_json(["tokenRequest"])
        token = await ws.receive_text()
        try:
            async with SessionLocal() as db:
                try:
                    user = await get_current_user(token, db)
                except HTTPException:
                    await ws.close(CloseCode.INTERNAL_ERROR, "authentication failed")
                    return None
        finally:
            await db.close()

        await ws.send_json(["auth"])
        return user

    async def connect(self, ws: WebSocket) -> Users | None:
        await ws.accept()
        user = await self.auth_user(ws)
        if user is None:
            return None

        old_ws = self.active_connections.get(user.username)
        if old_ws is not None:
            # if user is already connected disconnect old session
            print(old_ws.client_state, old_ws.application_state)
            try:
                await old_ws.send_json(
                    ["disconnected", {"details": "Logged in from elsewhere"}]
                )
                await old_ws.close(
                    CloseCode.POLICY_VIOLATION, "logged in from elsewhere"
                )
            except RuntimeError:
                pass
            await self.disconnect(user.username, old_ws)
        self.active_connections[user.username] = ws
        await ws.send_json(["connected"])
        return user

    async def disconnect(self, username: str, ws: WebSocket):
        if (
            username in self.active_connections
            and self.active_connections.get(username) == ws
        ):
            del self.active_connections[username]

    async def send_personal_message(self, username: str, msg: Any):
        ws = self.active_connections.get(username)
        if ws is None:
            raise WebSocketException(
                404, f"Connection with username {username} not found"
            )
        await ws.send_json(msg)

    async def broadcast(self, msg: str):
        for ws in self.active_connections.values():
            await ws.send_text(msg)
