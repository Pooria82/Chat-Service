import os
from datetime import datetime, timezone
from typing import List

import aiofiles
from fastapi import HTTPException, status, UploadFile
from motor.motor_asyncio import AsyncIOMotorCollection

from app.crud import create_chat_room, get_chat_room_by_id, create_message, get_private_chats_from_db
from app.models import UserInDB
from app.schemas import ChatRoomCreateSchema, ChatRoomResponseSchema, MessageCreateSchema, MessageResponseSchema
from app.services.connection_manager import ConnectionManager, SocketIOMessage
from app.services.user_status_service import UserStatusService


class ChatService:
    def __init__(self, db_chat_rooms: AsyncIOMotorCollection, connection_manager: ConnectionManager,
                 user_status_service: UserStatusService):
        self.db_chat_rooms = db_chat_rooms
        self.connection_manager = connection_manager
        self.user_status_service = user_status_service

    async def create_new_chat_room(self, chat_room: ChatRoomCreateSchema,
                                   current_user: UserInDB) -> ChatRoomResponseSchema:
        if current_user.email not in chat_room.members:
            chat_room.members.append(current_user.email)
        new_chat_room = await create_chat_room(self.db_chat_rooms, chat_room)

        chat_room_id = str(new_chat_room.id)
        new_chat_room_dict = new_chat_room.model_dump()
        new_chat_room_dict["id"] = chat_room_id

        return ChatRoomResponseSchema(**new_chat_room_dict)

    async def get_chat_room(self, room_id: str, current_user: UserInDB) -> ChatRoomResponseSchema:
        try:
            chat_room = await get_chat_room_by_id(self.db_chat_rooms, room_id)
            if not chat_room:
                print(f"Chat room not found: {room_id}")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat room not found")
            if current_user.email not in chat_room.members:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

            chat_room_dict = {
                "id": str(chat_room.id),
                "name": chat_room.name,
                "members": chat_room.members,
                "messages": [
                    {
                        **message.model_dump(),
                        "timestamp": message.timestamp.isoformat() if isinstance(message.timestamp,
                                                                                 datetime) else message.timestamp
                    }
                    for message in chat_room.messages or []
                ]
            }
            return ChatRoomResponseSchema(**chat_room_dict)
        except Exception as e:
            print(f"Error in get_chat_room: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Failed to retrieve chat room")

    async def create_message(self, room_id: str, message: MessageCreateSchema,
                             current_user: UserInDB) -> MessageResponseSchema:
        """Create a new message in a specific chat room."""
        try:
            chat_room = await get_chat_room_by_id(self.db_chat_rooms, room_id)
            if chat_room is None or current_user.email not in chat_room.members:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Chat room not found or access denied")

            # Prepare message data, ensuring the timestamp is always set
            message_data = {
                "sender": current_user.email,
                "content": message.content,
                "timestamp": message.timestamp or datetime.now(timezone.utc)
            }

            # Create a MessageCreateSchema instance
            message = MessageCreateSchema(**message_data)

            new_message = await create_message(self.db_chat_rooms, room_id, message)

            new_message_dict = {
                "id": str(new_message.id),
                "sender": new_message.sender,
                "content": new_message.content,
                "timestamp": new_message.timestamp.isoformat()
            }

            socket_message = SocketIOMessage(
                sender=new_message.sender,
                content=new_message.content,
                timestamp=new_message.timestamp.isoformat()
            )
            await self.connection_manager.broadcast(room_id, socket_message)

            return MessageResponseSchema(**new_message_dict)
        except Exception as e:
            print(f"Error in create_message: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create message")

    async def get_private_chats(self, current_user: UserInDB) -> List[dict]:
        try:
            private_chats = await get_private_chats_from_db(self.db_chat_rooms, current_user.id)
            for chat in private_chats:
                chat["is_online"] = self.user_status_service.is_user_online(chat["other_user_email"])
            return private_chats
        except Exception as e:
            print(f"Error in get_private_chats: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get private chats")

    async def get_all_messages(self, room_id: str, current_user: UserInDB) -> List[MessageResponseSchema]:
        try:
            chat_room = await get_chat_room_by_id(self.db_chat_rooms, room_id)
            if chat_room is None or current_user.email not in chat_room.members:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Chat room not found or access denied")

            messages = chat_room.messages or []

            messages_response = [
                MessageResponseSchema(**{
                    "id": str(message.id),
                    "sender": message.sender,  # This ensures the sender is included
                    "content": message.content,
                    "timestamp": message.timestamp.isoformat() if isinstance(message.timestamp,
                                                                             datetime) else message.timestamp
                })
                for message in messages
            ]

            return messages_response
        except Exception as e:
            print(f"Error in get_all_messages: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get messages")

    @staticmethod
    async def save_media(file: UploadFile) -> str:
        try:
            media_directory = "media"
            os.makedirs(media_directory, exist_ok=True)
            file_location = os.path.join(media_directory, file.filename)
            async with aiofiles.open(file_location, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
            return file_location
        except Exception as e:
            print(f"Error saving media: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save media")
