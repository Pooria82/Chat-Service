from datetime import datetime
from typing import List, Dict

import socketio
from pydantic import BaseModel


class SocketIOMessage(BaseModel):
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
        self.sio = socketio.AsyncServer(async_mode='asgi')
        self.active_connections: Dict[str, List[str]] = {}

    async def connect(self, room_id: str, sid: str):
        print(f"[LOG] Connecting sid {sid} to room {room_id}")
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(sid)
        await self.sio.enter_room(sid, room_id)

    async def disconnect(self, room_id: str, sid: str):
        print(f"[LOG] Disconnecting sid {sid} from room {room_id}")
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(sid)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
        await self.sio.leave_room(sid, room_id)

    async def broadcast(self, room_id: str, message: SocketIOMessage):
        print(f"[LOG] Broadcasting message to room {room_id}: {message.model_dump()}")
        if room_id in self.active_connections:
            message_json = message.model_dump()
            await self.sio.emit('broadcast_message', message_json, room=room_id)


# Initialize the connection manager
connection_manager = ConnectionManager()
sio = connection_manager.sio
