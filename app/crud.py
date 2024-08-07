from typing import List, Optional

from bson import ObjectId
from passlib.context import CryptContext
from pymongo.collection import Collection

from app.models import UserInDB, MessageInDB, ChatRoomInDB
from app.schemas import UserCreateSchema, MessageCreateSchema, ChatRoomCreateSchema

# Setup password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hashes a password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


# Helper functions to convert MongoDB documents to Pydantic models
def document_to_dict(doc) -> dict:
    """Converts MongoDB document to dictionary."""
    if doc:
        doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
        return dict(doc)  # Ensure it's a standard dictionary
    return {}


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
def create_user(db: Collection, user: UserCreateSchema) -> UserInDB:
    """Create a new user in the database."""
    user_dict = user.model_dump()  # Use model_dump instead of dict
    user_dict['hashed_password'] = hash_password(user.password)  # Hash the password
    result = db.insert_one(user_dict)
    created_user = db.find_one({"_id": result.inserted_id})
    return user_from_doc(created_user) if created_user else None


def get_user_by_email(db: Collection, email: str) -> Optional[UserInDB]:
    """Get a user by email."""
    user = db.find_one({"email": email})
    return user_from_doc(user) if user else None


def verify_user_password(db: Collection, email: str, password: str) -> bool:
    """Verify a user's password."""
    user = get_user_by_email(db, email)
    return user and verify_password(password, user.hashed_password)


# Message CRUD operations
def create_message(db: Collection, room_id: str, message: MessageCreateSchema) -> MessageInDB | None:
    """Create a new message in a specific chat room."""
    message_dict = message.model_dump()  # Use model_dump instead of dict
    db.update_one(
        {"_id": ObjectId(room_id)},
        {"$push": {"messages": message_dict}}
    )
    # Fetch the updated chat room to find the new message
    updated_room = db.find_one({"_id": ObjectId(room_id)})
    if updated_room and "messages" in updated_room:
        # Assuming that the message has a unique identifier, or we can search for it in the updated room
        for msg in updated_room["messages"]:
            if msg.get('_id') == message_dict['_id']:
                return message_from_doc(msg)
    return None


def get_messages(db: Collection, room_id: str) -> List[MessageInDB]:
    """Get all messages in a specific chat room."""
    room = db.find_one({"_id": ObjectId(room_id)})
    if room and "messages" in room:
        return [message_from_doc(msg) for msg in room["messages"]]
    return []


# Chat Room CRUD operations
def create_chat_room(db: Collection, chat_room: ChatRoomCreateSchema) -> ChatRoomInDB:
    """Create a new chat room."""
    chat_room_dict = chat_room.model_dump()  # Use model_dump instead of dict
    result = db.insert_one(chat_room_dict)
    created_room = db.find_one({"_id": result.inserted_id})
    return chat_room_from_doc(created_room) if created_room else None


def get_chat_room_by_id(db: Collection, room_id: str) -> Optional[ChatRoomInDB]:
    """Get a chat room by its ID."""
    room = db.find_one({"_id": ObjectId(room_id)})
    return chat_room_from_doc(room) if room else None
