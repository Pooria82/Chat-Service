# app/services/chat_service.py

from typing import List

from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorCollection

from app.crud import create_chat_room, get_chat_room_by_id, create_message, get_messages
from app.models import UserInDB
from app.schemas import ChatRoomCreateSchema, ChatRoomResponseSchema, MessageCreateSchema, MessageResponseSchema


class ChatService:
    def __init__(self, db: AsyncIOMotorCollection):
        self.db_chat_rooms = db["chat_rooms"]

    async def create_new_chat_room(self, chat_room: ChatRoomCreateSchema,
                                   current_user: UserInDB) -> ChatRoomResponseSchema:
        """Create a new chat room and add the current user as a member."""
        chat_room.members.append(current_user.email)
        new_chat_room = await create_chat_room(self.db_chat_rooms, chat_room)
        return ChatRoomResponseSchema(**new_chat_room.model_dump())  # Convert to ChatRoomResponseSchema

    async def get_chat_room(self, room_id: str, current_user: UserInDB) -> ChatRoomResponseSchema:
        """Get a specific chat room by its ID."""
        chat_room = await get_chat_room_by_id(self.db_chat_rooms, room_id)
        if chat_room is None or current_user.email not in chat_room.members:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat room not found or access denied")
        return ChatRoomResponseSchema(**chat_room.model_dump())  # Convert to ChatRoomResponseSchema

    async def create_new_message(self, room_id: str, message: MessageCreateSchema,
                                 current_user: UserInDB) -> MessageResponseSchema:
        """Create a new message in a specific chat room."""
        chat_room = await get_chat_room_by_id(self.db_chat_rooms, room_id)
        if chat_room is None or current_user.email not in chat_room.members:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat room not found or access denied")
        message.sender = current_user.email  # Set the sender of the message to the current user
        new_message = await create_message(self.db_chat_rooms, room_id, message)
        return MessageResponseSchema(**new_message.model_dump())  # Convert to MessageResponseSchema

    async def get_all_messages(self, room_id: str, current_user: UserInDB) -> List[MessageResponseSchema]:
        """Get all messages in a specific chat room."""
        chat_room = await get_chat_room_by_id(self.db_chat_rooms, room_id)
        if chat_room is None or current_user.email not in chat_room.members:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat room not found or access denied")
        messages = await get_messages(self.db_chat_rooms, room_id)
        return [MessageResponseSchema(**message.model_dump()) for message in
                messages]  # Convert each message to MessageResponseSchema
