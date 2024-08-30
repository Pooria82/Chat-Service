from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field


# User schemas
class UserBaseSchema(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreateSchema(UserBaseSchema):
    password: str


class UserResponseSchema(BaseModel):
    id: str
    username: str
    email: str

    class Config:
        from_attributes = True


class UserInDB(UserBaseSchema):
    id: str
    hashed_password: str


# Message schemas
class MessageBaseSchema(BaseModel):
    content: str
    timestamp: str


class MessageCreateSchema(BaseModel):
    sender: str
    content: str
    timestamp: Optional[datetime] = Field(None)


class MessageResponseSchema(MessageBaseSchema):
    id: str

    class Config:
        from_attributes = True


# Chat room schemas
class ChatRoomBaseSchema(BaseModel):
    name: str
    members: List[str]


class ChatRoomCreateSchema(ChatRoomBaseSchema):
    members: List[str] = []


class ChatRoomResponseSchema(ChatRoomBaseSchema):
    id: str
    messages: List[MessageResponseSchema] = []

    class Config:
        from_attributes = True


class PrivateChatResponseSchema(BaseModel):
    id: str
    other_user_email: str
    is_online: bool

    class Config:
        from_attributes = True


# Authentication schemas
class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class TokenDataSchema(BaseModel):
    email: str
