# app/services/connection_manager.py

from datetime import datetime
from typing import List, Dict

from fastapi import WebSocket
from pydantic import BaseModel


class WebSocketMessage(BaseModel):
    sender: str
    content: str
    timestamp: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()  # Convert datetime to ISO 8601 format
        }


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, room_id: str, websocket: WebSocket):
        """Add a websocket connection to a chat room."""
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, room_id: str, websocket: WebSocket):
        """Remove a websocket connection from a chat room."""
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    @staticmethod
    async def send_personal_message(message: WebSocketMessage, websocket: WebSocket):
        """Send a personal message to a websocket connection."""
        await websocket.send_text(message.model_dump_json())  # Convert WebSocketMessage to JSON and send

    async def broadcast(self, room_id: str, message: WebSocketMessage):
        """Broadcast a message to all websocket connections in a chat room."""
        if room_id in self.active_connections:
            message_json = message.model_dump_json()  # Convert WebSocketMessage to JSON
            for connection in self.active_connections[room_id]:
                await connection.send_text(message_json)
