# app/routers/websocket.py

from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from app.crud import create_message, get_chat_room_by_id, get_messages
from app.dependencies import get_db, get_current_user
from app.models import UserInDB
from app.schemas import MessageCreateSchema, MessageResponseSchema
from app.services.connection_manager import ConnectionManager

router = APIRouter()

manager = ConnectionManager()


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Process incoming message
            message_data = MessageCreateSchema(content=data, sender="Anonymous")  # Adjust as needed
            db_chat_rooms: AsyncIOMotorCollection = db["chat_rooms"]
            new_message = await create_message(db_chat_rooms, room_id, message_data)
            if new_message:
                response_message = MessageResponseSchema(**new_message.model_dump())
                await manager.broadcast(response_message.model_dump_json())
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"Error: {e}")


@router.get("/chat_rooms/{room_id}/messages", response_model=List[MessageResponseSchema])
async def get_all_messages(
        room_id: str,
        db: AsyncIOMotorDatabase = Depends(get_db),
        current_user: UserInDB = Depends(get_current_user)
):
    """Get all messages in a specific chat room."""
    db_chat_rooms: AsyncIOMotorCollection = db["chat_rooms"]
    chat_room = await get_chat_room_by_id(db_chat_rooms, room_id)
    if chat_room is None or current_user.email not in chat_room.members:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat room not found or access denied")
    messages = await get_messages(db_chat_rooms, room_id)
    return messages
