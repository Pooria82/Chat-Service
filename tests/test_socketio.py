# tests/test_socketio.py

import pytest
import socketio
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_socketio_connection(socket_client):
    client = socket_client
    await client.connect('http://localhost:8000/ws', headers={'Authorization': 'Bearer YOUR_TEST_TOKEN'})
    assert client.connected

    # Test sending a message
    await client.emit('chat_message', {'room': 'test_room', 'message': 'test message'})
    response = await client.call('chat_response')
    assert response == {'message': 'test message'}


@pytest.mark.asyncio
async def test_send_message(async_client: AsyncClient, clear_db):
    # Sign up a new user
    response = await async_client.post("/auth/signup", json={
        "username": "testuser",
        "email": "testchat@example.com",
        "password": "password123"
    })
    assert response.status_code == 200

    # Log in the user
    response = await async_client.post("/auth/login", data={
        "username": "testchat@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Create a chat room
    response = await async_client.post("/chat/chat_rooms/", json={
        "name": "Test Room",
        "members": ["testchat@example.com"]
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    room_id = response.json()["id"]

    # Connect to the socket.io server
    client = socketio.AsyncClient()
    await client.connect('http://localhost:8000/ws', headers={"Authorization": f"Bearer {token}"})

    # Send a message to the chat room
    await client.emit('chat_message', {'room': room_id, 'message': 'Hello, world!'})
    response = await client.call('chat_response')
    assert response == {'message': 'Hello, world!'}

    # Disconnect the socket.io client
    await client.disconnect()
