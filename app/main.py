from fastapi import FastAPI

from app.routers import auth, chat, websocket

app = FastAPI()

app.include_router(auth.router, prefix="/auth")
app.include_router(chat.router, prefix="/chat")
app.include_router(websocket.router)
