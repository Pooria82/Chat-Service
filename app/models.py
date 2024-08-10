from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr


# Base user model
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserInDB(UserBase):
    id: str  # MongoDB document ID
    hashed_password: str


# Chat message model
class MessageBase(BaseModel):
    sender: str
    content: str
    timestamp: datetime


class MessageInDB(MessageBase):
    id: str  # MongoDB document ID


# Chat room model
class ChatRoomBase(BaseModel):
    name: str
    members: List[str]  # List of user emails


class ChatRoomInDB(ChatRoomBase):
    id: str  # MongoDB document ID
    messages: List[MessageInDB]  # Messages associated with the chat room
