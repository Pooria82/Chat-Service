import datetime
from typing import List

from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import get_db, get_current_user
from app.models import UserInDB
from app.schemas import ChatRoomCreateSchema, ChatRoomResponseSchema, MessageCreateSchema, MessageResponseSchema
from app.services.chat_service import ChatService
from app.services.connection_manager import connection_manager, sio

router = APIRouter()


def custom_jsonable_encoder(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()  # Converts datetime to ISO 8601 format with +00:00
    if isinstance(obj, datetime.date):
        return obj.isoformat()  # Converts date to ISO 8601 format
    return jsonable_encoder(obj)


# Dependency to inject ChatService with necessary parameters
def get_chat_service(db: AsyncIOMotorDatabase = Depends(get_db)):
    db_chat_rooms = db["chat_rooms"]  # Extract the specific collection from the database
    return ChatService(db_chat_rooms=db_chat_rooms, connection_manager=connection_manager)


@router.post("/chat_rooms/", response_model=ChatRoomResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_new_chat_room(
        chat_room: ChatRoomCreateSchema,
        chat_service: ChatService = Depends(get_chat_service),
        current_user: UserInDB = Depends(get_current_user)
):
    """Create a new chat room."""
    chat_room.members.append(current_user.email)  # Add the current user to the chat room members
    new_chat_room = await chat_service.create_new_chat_room(chat_room, current_user)
    return new_chat_room


@router.get("/chat_rooms/{room_id}", response_model=ChatRoomResponseSchema)
async def get_chat_room(
        room_id: str,
        chat_service: ChatService = Depends(get_chat_service),
        current_user: UserInDB = Depends(get_current_user)
):
    """Get a specific chat room by its ID."""
    chat_room = await chat_service.get_chat_room(room_id, current_user)
    return chat_room


@router.post("/chat_rooms/{room_id}/messages", response_model=MessageResponseSchema,
             status_code=status.HTTP_201_CREATED)
async def create_new_message(
        room_id: str,
        message: MessageCreateSchema,
        chat_service: ChatService = Depends(get_chat_service),
        current_user: UserInDB = Depends(get_current_user)
):
    """Create a new message in a specific chat room."""
    new_message = await chat_service.create_new_message(room_id, message, current_user)

    # Emit the message to the chat room via Socket.IO
    await sio.emit('chat_response', {'room_id': room_id, 'message': custom_jsonable_encoder(message)}, room=room_id)

    return new_message


@router.get("/chat_rooms/{room_id}/messages", response_model=List[MessageResponseSchema])
async def get_all_messages(
        room_id: str,
        chat_service: ChatService = Depends(get_chat_service),
        current_user: UserInDB = Depends(get_current_user)
):
    """Get all messages in a specific chat room."""
    messages = await chat_service.get_all_messages(room_id, current_user)
    return messages


@router.post("/upload_media/")
async def upload_media(
        file: UploadFile = File(...),
        chat_service: ChatService = Depends(get_chat_service)  # Injecting ChatService dependency
):
    """Upload a media file."""
    file_url = await chat_service.save_media(file)
    return {"file_url": file_url}
