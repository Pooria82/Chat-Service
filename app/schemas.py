from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr


# User schemas
class UserBaseSchema(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreateSchema(UserBaseSchema):
    password: str


class UserResponseSchema(UserBaseSchema):
    id: str  # MongoDB document ID


# Message schemas
class MessageBaseSchema(BaseModel):
    sender: str
    content: str
    timestamp: datetime


class MessageCreateSchema(MessageBaseSchema):
    pass


class MessageResponseSchema(MessageBaseSchema):
    id: str  # MongoDB document ID


# Chat room schemas
class ChatRoomBaseSchema(BaseModel):
    name: str
    members: List[str]  # List of user emails


class ChatRoomCreateSchema(ChatRoomBaseSchema):
    pass


class ChatRoomResponseSchema(ChatRoomBaseSchema):
    id: str  # MongoDB document ID
    messages: List[MessageResponseSchema]  # List of messages in the chat room


# Authentication schemas
class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class TokenDataSchema(BaseModel):
    email: str
