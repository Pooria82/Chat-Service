from fastapi import FastAPI
from socketio import ASGIApp

from app.routers import auth, chat, socketio_routes
from app.services.connection_manager import sio

app = FastAPI()

# Include the routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(socketio_routes.router, prefix="/ws", tags=["socketio"])

# Attach SocketIO to FastAPI app
sio_app = ASGIApp(sio, other_asgi_app=app)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Chat Service API"}


# If running the application directly, use Uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(sio_app, host="0.0.0.0", port=8000)
