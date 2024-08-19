from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection

from app.dependencies import get_current_user, get_db
from app.services.connection_manager import SocketIOMessage
from app.services.connection_manager import connection_manager, sio

router = APIRouter()


@sio.event
async def connect(sid, environ, db: AsyncIOMotorCollection = Depends(get_db)):
    token = environ.get('HTTP_AUTHORIZATION', None)
    if token is None:
        return False  # Reject the connection if no token is provided
    token = token.replace('Bearer ', '')
    try:
        user = await get_current_user(token, db)
    except HTTPException:
        return False  # Reject the connection if token validation fails
    # Store user information with the connection
    await connection_manager.connect(user.email, sid)
    print(f'Client {sid} connected as {user.email}')


@sio.event
async def disconnect(sid):
    # Logic to determine the room_id should be added here
    room_id = "room_id_example"
    await connection_manager.disconnect(room_id, sid)
    print(f'Client {sid} disconnected')


@sio.event
async def chat_message(sid, data):
    room = data.get('room')
    message_content = data.get('message')
    if room and message_content:
        message = SocketIOMessage(sender=sid, content=message_content, timestamp=datetime.now(timezone.utc))
        await connection_manager.broadcast(room, message)
    else:
        await sio.emit('error', {'message': 'Invalid data'}, room=sid)
