import socketio
from fastapi import FastAPI

from .crud import create_message
from .models import Message

sio = socketio.Server()
app = FastAPI()


@sio.on("join")
def join(sid, data):
    sio.enter_room(sid, data["room"])


@sio.on("message")
def handle_message(sid, data):
    message = Message(**data)
    create_message(message)
    sio.send(data, room=message.room_id)


app = socketio.ASGIApp(sio)
