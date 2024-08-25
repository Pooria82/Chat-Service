from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.database import db
from app.dependencies import get_current_user
from app.services.connection_manager import SocketIOMessage
from app.services.connection_manager import connection_manager, sio
from app.services.user_status_service import UserStatusService

router = APIRouter()

user_status_service = UserStatusService()


@sio.event
async def connect(sid, environ):
    token = environ.get('HTTP_AUTHORIZATION', None)
    if token is None:
        return False  # Reject the connection if no token is provided

    token = token.replace('Bearer ', '')
    try:
        users_collection = db['users']
        user = await get_current_user(token, users_collection)
    except HTTPException:
        return False  # Reject the connection if token validation fails

    # Store user information with the connection
    await connection_manager.connect(user.email, sid)

    # Mark the user as online
    user_status_service.set_user_online(user.email, sid)

    print(f"[LOG] User {user.email} connected. SID: {sid}")


@sio.event
async def disconnect(sid):
    user_email = None
    for email, sids in user_status_service.active_connections.items():
        if sid in sids:
            user_email = email
            break

    if user_email:
        # Logic to determine the room_id should be added here
        room_id = "room_id_example"
        await connection_manager.disconnect(room_id, sid)

        user_status_service.set_user_offline(user_email, sid)

        print(f"[LOG] User {user_email} disconnected. SID: {sid}")


@sio.event
async def chat_message(sid, data):
    room = data.get('room')
    message_content = data.get('message')
    if room and message_content:
        message = SocketIOMessage(sender=sid, content=message_content, timestamp=datetime.now(timezone.utc))
        await connection_manager.broadcast(room, message)
        await sio.emit('chat_response', {'status': 'received', 'message': message_content}, room=sid)
    else:
        await sio.emit('error', {'message': 'Invalid data'}, room=sid)


@sio.event
async def get_online_users(sid):
    online_users = user_status_service.online_users  # Accessing the property directly
    await sio.emit('online_users', list(online_users), room=sid)

