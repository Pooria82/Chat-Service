from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from bson import ObjectId
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorCollection
from passlib.context import CryptContext

from app.models import UserInDB, MessageInDB, ChatRoomInDB
from app.schemas import UserCreateSchema, MessageCreateSchema, ChatRoomCreateSchema, UserResponseSchema

# Setup password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hashes a password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


# Helper functions to convert MongoDB documents to Pydantic models
def document_to_dict(document: dict) -> Dict[str, Any]:
    """Converts MongoDB document to a dictionary."""
    doc_dict = dict(document)

    # Convert ObjectId to string for top-level _id
    if '_id' in doc_dict:
        doc_dict['id'] = str(doc_dict.pop('_id'))

    # Convert ObjectId to string for messages if messages is a list
    if 'messages' in doc_dict and isinstance(doc_dict['messages'], list):
        for message in doc_dict['messages']:
            if isinstance(message, dict) and '_id' in message:
                message['id'] = str(message.pop('_id'))

    return doc_dict


def user_from_doc(doc) -> UserInDB:
    """Converts MongoDB user document to Pydantic UserInDB model."""
    return UserInDB(**document_to_dict(doc))


def message_from_doc(doc) -> MessageInDB:
    """Converts MongoDB message document to Pydantic MessageInDB model."""
    return MessageInDB(**document_to_dict(doc))


def chat_room_from_doc(doc) -> ChatRoomInDB:
    """Converts MongoDB chat room document to Pydantic ChatRoomInDB model."""
    return ChatRoomInDB(**document_to_dict(doc))


# User CRUD operations
async def create_user(db: AsyncIOMotorCollection, user: UserCreateSchema) -> UserResponseSchema:
    """Create a new user in the database."""
    user_dict = jsonable_encoder(user)
    user_dict = dict(user_dict)
    user_dict['hashed_password'] = hash_password(user.password)  # Hash the password
    del user_dict['password']  # Remove the plain password
    result = await db.insert_one(user_dict)
    return UserResponseSchema(**document_to_dict(await db.find_one({"_id": result.inserted_id})))


async def get_user_by_email(db: AsyncIOMotorCollection, email: str) -> Optional[UserInDB]:
    """Get a user by email."""
    user = await db.find_one({"email": email})
    if user:
        user_dict = document_to_dict(user)
        return UserInDB(**user_dict)  # Ensure that user_dict is a dict
    return None


async def verify_user_password(db: AsyncIOMotorCollection, email: str, password: str) -> bool:
    """Verify a user's password."""
    user = await get_user_by_email(db, email)
    if user and verify_password(password, user.hashed_password):
        return True
    return False


# Message CRUD operations
async def create_message(db: AsyncIOMotorCollection, room_id: str, message: MessageCreateSchema) -> MessageInDB:
    """Create a new message in a specific chat room."""
    message_dict = jsonable_encoder(message)
    message_dict = dict(message_dict)
    message_dict['timestamp'] = datetime.now(timezone.utc)
    message_dict['_id'] = ObjectId()  # Generate a unique ObjectId for the message
    update_result = await db.update_one(
        {"_id": ObjectId(room_id)},
        {"$push": {"messages": message_dict}}
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat room not found")
    return message_from_doc(message_dict)


async def get_messages(db: AsyncIOMotorCollection, room_id: str) -> List[MessageInDB]:
    """Get all messages in a specific chat room."""
    room = await db.find_one({"_id": ObjectId(room_id)})
    if room and "messages" in room:
        return [message_from_doc(msg) for msg in room["messages"]]
    return []


# Chat Room CRUD operations
async def create_chat_room(db: AsyncIOMotorCollection, chat_room: ChatRoomCreateSchema) -> ChatRoomInDB:
    """Create a new chat room."""
    chat_room_dict = jsonable_encoder(chat_room)
    chat_room_dict = dict(chat_room_dict)
    chat_room_dict['messages'] = []  # Ensure messages field is initialized
    result = await db.insert_one(chat_room_dict)
    return chat_room_from_doc(await db.find_one({"_id": result.inserted_id}))


async def get_chat_room_by_id(db: AsyncIOMotorCollection, room_id: str) -> Optional[ChatRoomInDB]:
    """Get a chat room by its ID."""
    room = await db.find_one({"_id": ObjectId(room_id)})
    if room:
        return chat_room_from_doc(room)
    return None
