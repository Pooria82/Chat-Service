from fastapi import FastAPI

from app.routers import auth, chat, websocket

app = FastAPI()

# Include the routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Chat Service API"}


# If running the application directly, use Uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
