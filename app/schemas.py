from typing import Optional, List

from pydantic import BaseModel, EmailStr


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
        orm_mode = True


class UserInDB(UserBaseSchema):
    id: str  # MongoDB document ID
    hashed_password: str


# Message schemas
class MessageBaseSchema(BaseModel):
    sender: str
    content: str
    timestamp: str  # Change from datetime to str


class MessageCreateSchema(MessageBaseSchema):
    pass  # No additional fields needed, inherits from MessageBaseSchema


class MessageResponseSchema(MessageBaseSchema):
    id: str  # MongoDB document ID

    class Config:
        orm_mode = True


# Chat room schemas
class ChatRoomBaseSchema(BaseModel):
    name: str
    members: List[str]  # List of user emails


class ChatRoomCreateSchema(ChatRoomBaseSchema):
    members: List[str] = []


class ChatRoomResponseSchema(ChatRoomBaseSchema):
    id: str  # MongoDB document ID
    messages: List[MessageResponseSchema] = []  # List of messages in the chat room

    class Config:
        orm_mode = True


# Authentication schemas
class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class TokenDataSchema(BaseModel):
    email: str
