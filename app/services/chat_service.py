import os
from typing import List

import aiofiles
from fastapi import HTTPException, status, UploadFile
from motor.motor_asyncio import AsyncIOMotorCollection

from app.crud import create_chat_room, get_chat_room_by_id, create_message, get_messages
from app.models import UserInDB
from app.schemas import ChatRoomCreateSchema, ChatRoomResponseSchema, MessageCreateSchema, MessageResponseSchema
from app.services.connection_manager import ConnectionManager, SocketIOMessage


class ChatService:
    def __init__(self, db_chat_rooms: AsyncIOMotorCollection, connection_manager: ConnectionManager):
        self.db_chat_rooms = db_chat_rooms
        self.connection_manager = connection_manager

    async def create_new_chat_room(self, chat_room: ChatRoomCreateSchema,
                                   current_user: UserInDB) -> ChatRoomResponseSchema:
        """Create a new chat room and add the current user as a member."""
        if current_user.email not in chat_room.members:
            chat_room.members.append(current_user.email)
        new_chat_room = await create_chat_room(self.db_chat_rooms, chat_room)

        chat_room_id = str(new_chat_room.id)

        new_chat_room_dict = new_chat_room.model_dump()
        new_chat_room_dict["id"] = chat_room_id

        return ChatRoomResponseSchema(**new_chat_room_dict)

    async def get_chat_room(self, room_id: str, current_user: UserInDB) -> ChatRoomResponseSchema:
        """Get a specific chat room by its ID."""
        chat_room = await get_chat_room_by_id(self.db_chat_rooms, room_id)

        # Check if the chat room exists and the user is a member
        if chat_room is None or current_user.email not in chat_room.members:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat room not found or access denied")

        # Convert ChatRoomInDB to dictionary
        chat_room_dict = {
            "id": str(chat_room.id),
            "name": chat_room.name,
            "members": chat_room.members,
            "messages": chat_room.messages or []
        }

        return ChatRoomResponseSchema(**chat_room_dict)

    async def create_new_message(self, room_id: str, message: MessageCreateSchema,
                                 current_user: UserInDB) -> MessageResponseSchema:
        """Create a new message in a specific chat room."""
        chat_room = await get_chat_room_by_id(self.db_chat_rooms, room_id)

        # Ensure chat_room is an instance of ChatRoomInDB
        if chat_room is None or current_user.email not in chat_room.members:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat room not found or access denied")

        # Set the sender of the message to the current user
        message.sender = current_user.email

        # Save the new message
        new_message = await create_message(self.db_chat_rooms, room_id, message)

        # Convert the new message to a dictionary
        new_message_dict = {
            "id": str(new_message.id),  # Access id with dot notation
            "sender": new_message.sender,  # Access sender with dot notation
            "content": new_message.content,  # Access content with dot notation
            "timestamp": new_message.timestamp.isoformat()  # Convert timestamp to ISO format
        }

        # Broadcast the new message to all clients in the room
        socket_message = SocketIOMessage(
            sender=new_message.sender,
            content=new_message.content,
            timestamp=new_message.timestamp.isoformat()  # Convert timestamp to ISO format
        )
        await self.connection_manager.broadcast(room_id, socket_message)

        return MessageResponseSchema(**new_message_dict)

    async def get_all_messages(self, room_id: str, current_user: UserInDB) -> List[MessageResponseSchema]:
        """Get all messages in a specific chat room."""
        chat_room = await get_chat_room_by_id(self.db_chat_rooms, room_id)

        # Ensure chat_room is an instance of ChatRoomInDB
        if chat_room is None or current_user.email not in chat_room.members:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat room not found or access denied")

        # Retrieve all messages in the chat room
        messages = await get_messages(self.db_chat_rooms, room_id)

        # Convert list of MessageInDB to list of MessageResponseSchema
        message_schemas = [
            MessageResponseSchema(
                id=str(message.id),  # Use dot notation for attributes
                sender=message.sender,
                content=message.content,
                timestamp=message.timestamp.isoformat()  # Ensure timestamp is in ISO format if it's a datetime object
            )
            for message in messages
        ]

        return message_schemas

    @staticmethod
    async def save_media(file: UploadFile) -> str:
        """Save the uploaded media file and return its file path."""
        media_directory = "media"
        os.makedirs(media_directory, exist_ok=True)  # Create directory if it doesn't exist
        file_location = os.path.join(media_directory, file.filename)
        async with aiofiles.open(file_location, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        return file_location
