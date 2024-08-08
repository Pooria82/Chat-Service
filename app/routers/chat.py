# app/routers/chat.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from app.crud import create_chat_room, get_chat_room_by_id, create_message, get_messages
from app.dependencies import get_db, get_current_user
from app.models import UserInDB
from app.schemas import ChatRoomCreateSchema, ChatRoomResponseSchema, MessageCreateSchema, MessageResponseSchema

router = APIRouter()


@router.post("/chat_rooms/", response_model=ChatRoomResponseSchema)
async def create_new_chat_room(
        chat_room: ChatRoomCreateSchema,
        db: AsyncIOMotorDatabase = Depends(get_db),
        current_user: UserInDB = Depends(get_current_user)
):
    """Create a new chat room."""
    chat_room.members.append(current_user.email)  # Add the current user to the chat room members
    db_chat_rooms: AsyncIOMotorCollection = db["chat_rooms"]
    new_chat_room = await create_chat_room(db_chat_rooms, chat_room)
    return new_chat_room


@router.get("/chat_rooms/{room_id}", response_model=ChatRoomResponseSchema)
async def get_chat_room(
        room_id: str,
        db: AsyncIOMotorDatabase = Depends(get_db),
        current_user: UserInDB = Depends(get_current_user)
):
    """Get a specific chat room by its ID."""
    db_chat_rooms: AsyncIOMotorCollection = db["chat_rooms"]
    chat_room = await get_chat_room_by_id(db_chat_rooms, room_id)
    if chat_room is None or current_user.email not in chat_room.members:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat room not found or access denied")
    return chat_room


@router.post("/chat_rooms/{room_id}/messages", response_model=MessageResponseSchema)
async def create_new_message(
        room_id: str,
        message: MessageCreateSchema,
        db: AsyncIOMotorDatabase = Depends(get_db),
        current_user: UserInDB = Depends(get_current_user)
):
    """Create a new message in a specific chat room."""
    db_chat_rooms: AsyncIOMotorCollection = db["chat_rooms"]
    chat_room = await get_chat_room_by_id(db_chat_rooms, room_id)
    if chat_room is None or current_user.email not in chat_room.members:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat room not found or access denied")
    message.sender = current_user.email  # Set the sender of the message to the current user
    new_message = await create_message(db_chat_rooms, room_id, message)
    return new_message


@router.get("/chat_rooms/{room_id}/messages", response_model=List[MessageResponseSchema])
async def get_all_messages(
        room_id: str,
        db: AsyncIOMotorDatabase = Depends(get_db),
        current_user: UserInDB = Depends(get_current_user)
):
    """Get all messages in a specific chat room."""
    db_chat_rooms: AsyncIOMotorCollection = db["chat_rooms"]
    chat_room = await get_chat_room_by_id(db_chat_rooms, room_id)
    if chat_room is None or current_user.email not in chat_room.members:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat room not found or access denied")
    messages = await get_messages(db_chat_rooms, room_id)
    return messages
