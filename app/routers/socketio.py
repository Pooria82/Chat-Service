from fastapi import APIRouter, HTTPException, FastAPI
from fastapi_socketio import SocketManager

from app.dependencies import get_current_user

app = FastAPI()
sio = SocketManager(app=app)

router = APIRouter()


@sio.on('connect')
async def connect(sid, environ):
    token = environ.get('HTTP_AUTHORIZATION', None)
    if token is None:
        return False  # Reject the connection if no token is provided
    token = token.replace('Bearer ', '')
    try:
        user = await get_current_user(token)
    except HTTPException:
        return False  # Reject the connection if token validation fails
    # Store user information with the connection
    sio.enter_room(sid, user.email)


@sio.on('disconnect')
async def disconnect(sid):
    print(f'Client {sid} disconnected')


@sio.on('chat_message')
async def handle_message(sid, data):
    room = data.get('room')
    message = data.get('message')
    if room and message:
        await sio.emit('chat_response', {'message': message}, room=room)
    else:
        await sio.emit('error', {'message': 'Invalid data'}, room=sid)
