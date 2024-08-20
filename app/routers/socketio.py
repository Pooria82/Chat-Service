from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.database import db
from app.dependencies import get_current_user
from app.services.connection_manager import SocketIOMessage
from app.services.connection_manager import connection_manager, sio

router = APIRouter()


@sio.event
async def connect(sid, environ):
    print(f"[LOG] Attempting to connect with sid: {sid}")
    token = environ.get('HTTP_AUTHORIZATION', None)
    if token is None:
        print(f"[LOG] Connection rejected for sid: {sid}, reason: No token provided")
        return False  # Reject the connection if no token is provided

    token = token.replace('Bearer ', '')
    try:
        users_collection = db['users']
        user = await get_current_user(token, users_collection)
        print(f"[LOG] User {user.email} authenticated successfully with sid: {sid}")
    except HTTPException as e:
        print(f"[LOG] Connection rejected for sid: {sid}, reason: {str(e)}")
        return False  # Reject the connection if token validation fails

    # Store user information with the connection
    await connection_manager.connect(user.email, sid)
    print(f"[LOG] Client {sid} connected as {user.email}")


@sio.event
async def disconnect(sid):
    print(f"[LOG] Disconnecting client with sid: {sid}")
    # Logic to determine the room_id should be added here
    room_id = "room_id_example"
    await connection_manager.disconnect(room_id, sid)
    print(f"[LOG] Client {sid} disconnected from room {room_id}")


@sio.event
async def chat_message(sid, data):
    room = data.get('room')
    message_content = data.get('message')
    if room and message_content:
        message = SocketIOMessage(sender=sid, content=message_content, timestamp=datetime.now(timezone.utc))
        print(f"[LOG] Broadcasting message to room {room}: {message.dict()}")
        await connection_manager.broadcast(room, message)

        print(
            f"[LOG] Sending chat response to sid: {sid}, response: {{'status': 'received', 'message': '{message_content}'}}")
        await sio.emit('chat_response', {'status': 'received', 'message': message_content}, room=sid)
    else:
        print(f"[LOG] Sending error to sid: {sid}")
        await sio.emit('error', {'message': 'Invalid data'}, room=sid)
