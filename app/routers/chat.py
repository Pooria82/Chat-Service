from datetime import datetime, timezone, date
from typing import List

from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import get_db, get_current_user
from app.models import UserInDB
from app.schemas import ChatRoomCreateSchema, ChatRoomResponseSchema, MessageCreateSchema, MessageResponseSchema, \
    PrivateChatResponseSchema
from app.services.chat_service import ChatService
from app.services.connection_manager import connection_manager, sio
from app.services.user_status_service import UserStatusService

router = APIRouter()


def custom_jsonable_encoder(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()  # Converts datetime to ISO 8601 format with +00:00
    if isinstance(obj, date):
        return obj.isoformat()  # Converts date to ISO 8601 format
    return jsonable_encoder(obj)


def get_chat_service(db: AsyncIOMotorDatabase = Depends(get_db), user_status_service: UserStatusService = Depends()):
    db_chat_rooms = db["chat_rooms"]
    return ChatService(db_chat_rooms=db_chat_rooms, connection_manager=connection_manager,
                       user_status_service=user_status_service)


@router.get("/private_chats/", response_model=List[PrivateChatResponseSchema])
async def get_private_chats(
        current_user: UserInDB = Depends(get_current_user),
        chat_service: ChatService = Depends(get_chat_service)
):
    """Get a list of private chats with online status."""
    private_chats = await chat_service.get_private_chats(current_user)
    return private_chats


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
        content: str = Form(...),
        file: UploadFile = File(None),  # Optional file
        chat_service: ChatService = Depends(get_chat_service),
        current_user: UserInDB = Depends(get_current_user)
):
    """Create a new message in a specific chat room, optionally with a file."""
    # Use the current user's email as the sender
    message_data = {"sender": current_user.email, "content": content}

    if file:
        # Save media file if provided and add to message content or handle separately
        file_url = await chat_service.save_media(file)
        message_data["content"] += f" [Media: {file_url}]"

    # Set the timestamp if it's not already in the message_data
    if 'timestamp' not in message_data:
        message_data['timestamp'] = datetime.now(timezone.utc)

    # Create the message object
    message = MessageCreateSchema(**message_data)
    new_message = await chat_service.create_message(room_id, message, current_user)

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
