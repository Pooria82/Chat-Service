from typing import List

from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorCollection

from app.crud import create_chat_room, get_chat_room_by_id, create_message, get_messages
from app.models import UserInDB
from app.schemas import ChatRoomCreateSchema, ChatRoomResponseSchema, MessageCreateSchema, MessageResponseSchema
from app.services.connection_manager import ConnectionManager, SocketIOMessage


class ChatService:
    def __init__(self, db: AsyncIOMotorCollection, connection_manager: ConnectionManager):
        self.db_chat_rooms = db["chat_rooms"]
        self.connection_manager = connection_manager

    async def create_new_chat_room(self, chat_room: ChatRoomCreateSchema,
                                   current_user: UserInDB) -> ChatRoomResponseSchema:
        """Create a new chat room and add the current user as a member."""
        chat_room.members.append(current_user.email)
        new_chat_room = await create_chat_room(self.db_chat_rooms, chat_room)
        # Convert ChatRoomInDB to dictionary
        new_chat_room_dict = {
            "id": str(new_chat_room["_id"]),
            "name": new_chat_room["name"],
            "members": new_chat_room["members"],
            "messages": new_chat_room.get("messages", [])
        }
        return ChatRoomResponseSchema(**new_chat_room_dict)

    async def get_chat_room(self, room_id: str, current_user: UserInDB) -> ChatRoomResponseSchema:
        """Get a specific chat room by its ID."""
        chat_room = await get_chat_room_by_id(self.db_chat_rooms, room_id)
        if chat_room is None or current_user.email not in chat_room["members"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat room not found or access denied")
        # Convert ChatRoomInDB to dictionary
        chat_room_dict = {
            "id": str(chat_room["_id"]),
            "name": chat_room["name"],
            "members": chat_room["members"],
            "messages": chat_room.get("messages", [])
        }
        return ChatRoomResponseSchema(**chat_room_dict)

    async def create_new_message(self, room_id: str, message: MessageCreateSchema,
                                 current_user: UserInDB) -> MessageResponseSchema:
        """Create a new message in a specific chat room."""
        chat_room = await get_chat_room_by_id(self.db_chat_rooms, room_id)
        if chat_room is None or current_user.email not in chat_room["members"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat room not found or access denied")
        message.sender = current_user.email  # Set the sender of the message to the current user
        new_message = await create_message(self.db_chat_rooms, room_id, message)
        # Convert MessageInDB to dictionary
        new_message_dict = {
            "id": str(new_message["_id"]),
            "sender": new_message["sender"],
            "content": new_message["content"],
            "timestamp": new_message["timestamp"]
        }
        # Broadcast the new message to all clients in the room
        socket_message = SocketIOMessage(
            sender=new_message["sender"],
            content=new_message["content"],
            timestamp=new_message["timestamp"]
        )
        await self.connection_manager.broadcast(room_id, socket_message)
        return MessageResponseSchema(**new_message_dict)

    async def get_all_messages(self, room_id: str, current_user: UserInDB) -> List[MessageResponseSchema]:
        """Get all messages in a specific chat room."""
        chat_room = await get_chat_room_by_id(self.db_chat_rooms, room_id)
        if chat_room is None or current_user.email not in chat_room["members"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat room not found or access denied")
        messages = await get_messages(self.db_chat_rooms, room_id)
        # Convert list of MessageInDB to list of dictionaries
        message_dicts = [
            {
                "id": str(message["_id"]),
                "sender": message["sender"],
                "content": message["content"],
                "timestamp": message["timestamp"]
            }
            for message in messages
        ]
        return [MessageResponseSchema(**msg_dict) for msg_dict in message_dicts]
