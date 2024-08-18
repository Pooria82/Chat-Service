from fastapi import FastAPI
from fastapi_socketio import SocketManager

from app.routers import auth, chat, socketio

app = FastAPI()

# Create a SocketManager instance
sio = SocketManager()


@app.on_event("startup")
async def startup_event():
    """Attach the SocketManager to the app on startup."""
    sio.attach(app)


@app.on_event("shutdown")
async def shutdown_event():
    """Perform any cleanup tasks on shutdown."""
    # No explicit detach method in SocketManager
    pass


# Include the routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(socketio.router, prefix="/ws", tags=["socketio"])


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Chat Service API"}


# If running the application directly, use Uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
