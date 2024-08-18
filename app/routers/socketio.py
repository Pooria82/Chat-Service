from fastapi import APIRouter, HTTPException
from fastapi_socketio import SocketManager

from app.dependencies import get_current_user

router = APIRouter()

# Create a SocketManager instance
sio = SocketManager()


# Define the startup and shutdown handlers directly in main.py
@router.on_event("startup")
async def startup_event():
    """Attach the SocketManager to the app on startup."""
    # SocketManager is attached in main.py
    pass


@router.on_event("shutdown")
async def shutdown_event():
    """Perform any cleanup tasks on shutdown."""
    # SocketManager is detached in main.py
    pass


@sio.on('connect')
async def connect(sid, environ):
    """Handle client connection."""
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
    print(f'Client {sid} connected as {user.email}')


@sio.on('disconnect')
async def disconnect(sid):
    """Handle client disconnection."""
    print(f'Client {sid} disconnected')
    # Additional cleanup if necessary


@sio.on('chat_message')
async def handle_message(sid, data):
    """Handle chat messages from clients."""
    room = data.get('room')
    message = data.get('message')
    if room and message:
        await sio.emit('chat_response', {'message': message}, room=room)
    else:
        await sio.emit('error', {'message': 'Invalid data'}, room=sid)
