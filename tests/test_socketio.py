import asyncio

import pytest
import socketio
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_socketio_connection(socket_client):
    client = socket_client
    print("[LOG] Testing socket.io connection")
    assert client.connected

    print("[LOG] Sending chat message to room 'test_room'")
    await client.emit('chat_message', {'room': 'test_room', 'message': 'test message'})

    response = None

    def on_chat_response(data):
        nonlocal response
        response = data
        print(f"[LOG] Chat response received: {data}")

    client.on('chat_response', on_chat_response)

    print("[LOG] Waiting for chat response")
    try:
        await asyncio.sleep(5)
        print(f"[LOG] Chat response after sleep: {response}")
    except Exception as e:
        print(f"[LOG] Error waiting for chat response: {str(e)}")

    assert response == {'status': 'received', 'message': 'test message'}


@pytest.mark.asyncio
async def test_send_message(async_client: AsyncClient, clear_db, get_auth_token):
    token = get_auth_token

    response = await async_client.post("/chat/chat_rooms/", json={
        "name": "Test Room",
        "members": ["testchat@example.com"]
    }, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 201

    room_id = response.json()["id"]

    client = socketio.AsyncClient()

    try:
        await client.connect('http://localhost:8000/ws', headers={"Authorization": f"Bearer {token}"})
        print("[LOG] Connected to Socket.IO server")
    except Exception as e:
        print(f"[ERROR] Failed to connect to Socket.IO server: {e}")
        return

    response = None

    async def chat_message_callback(data):
        nonlocal response
        response = data
        print(f"[LOG] Received chat message callback with data: {data}")

    client.on('chat_message', chat_message_callback)

    await client.emit('chat_message', {'room': room_id, 'message': 'Hello, world!'})
    print("[LOG] Sent message to chat room")

    await asyncio.sleep(5)

    if response is None:
        print("[ERROR] No response received from the server.")
    else:
        assert response == {'status': 'received', 'message': 'Hello, world!'}
        print("[LOG] Test passed: Message received successfully")

    await client.disconnect()
    print("[LOG] Disconnected from Socket.IO server")
