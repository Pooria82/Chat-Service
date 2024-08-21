import datetime

import pytest
from httpx import AsyncClient

from app.schemas import ChatRoomCreateSchema, MessageCreateSchema


# Helper function to sign up and log in
async def sign_up_and_login(async_client: AsyncClient, email: str, password: str):
    # Sign up a new user
    response = await async_client.post("/auth/signup", json={
        "username": "testuser",
        "email": email,
        "password": password
    })
    assert response.status_code == 201

    # Log in the user
    response = await async_client.post("/auth/login", data={
        "username": email,
        "password": password
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    return token


# Helper function to create a chat room
async def create_new_chat_room(async_client: AsyncClient, token: str, room_name: str):
    response = await async_client.post("/chat/chat_rooms/", json={
        "name": room_name
    }, headers={"Authorization": f"Bearer {token}"})

    # Print the response content for debugging
    print(response.json())

    assert response.status_code == 201
    chat_room_id = response.json().get("id")
    return chat_room_id


@pytest.mark.asyncio
async def test_create_chat_room(async_client: AsyncClient, clear_db):
    # Sign up and log in to get the token
    token = await sign_up_and_login(async_client, "testchat@example.com", "password123")

    # Create a new chat room
    chat_room_data = ChatRoomCreateSchema(name="Test Room", members=[])
    response = await async_client.post(
        "/chat/chat_rooms/",
        json=chat_room_data.model_dump(),  # Use model_dump()
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201

    # Verify the response data
    response_data = response.json()
    assert response_data["name"] == "Test Room"
    assert "id" in response_data
    assert "members" in response_data
    assert len(response_data["members"]) == 1  # Ensure the current user is added as a member


@pytest.mark.asyncio
async def test_get_chat_room(async_client: AsyncClient, clear_db):
    # Sign up and log in to get the token
    token = await sign_up_and_login(async_client, "testchat@example.com", "password123")

    # Create a new chat room to get its ID
    chat_room_data = ChatRoomCreateSchema(name="Test Room", members=[])
    create_response = await async_client.post(
        "/chat/chat_rooms/",
        json=chat_room_data.model_dump(),  # Use model_dump()
        headers={"Authorization": f"Bearer {token}"}
    )
    chat_room_id = create_response.json()["id"]

    # Get the created chat room
    response = await async_client.get(
        f"/chat/chat_rooms/{chat_room_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    # Check if the response status is 200 OK
    assert response.status_code == 200

    # Verify the response data
    response_data = response.json()
    assert response_data["id"] == chat_room_id
    assert response_data["name"] == "Test Room"


@pytest.mark.asyncio
async def test_create_message(async_client: AsyncClient, clear_db):
    # Sign up and log in to get the token
    token = await sign_up_and_login(async_client, "testchat@example.com", "password123")

    # Create a new chat room to get its ID
    chat_room_data = ChatRoomCreateSchema(name="Test Room", members=[])
    create_response = await async_client.post(
        "/chat/chat_rooms/",
        json=chat_room_data.model_dump(),
        headers={"Authorization": f"Bearer {token}"}
    )
    chat_room_id = create_response.json()["id"]

    # Create a new message
    timestamp = datetime.datetime.now().isoformat()  # Use ISO format for current datetime
    message_data = MessageCreateSchema(
        sender="testchat@example.com",
        content="Hello, world!",
        timestamp=timestamp  # Ensure this is a string
    )

    # Convert message_data to a JSON-compatible format
    json_message_data = message_data.model_dump()

    response = await async_client.post(
        f"/chat/chat_rooms/{chat_room_id}/messages",
        json=json_message_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["sender"] == "testchat@example.com"
    assert data["content"] == "Hello, world!"


@pytest.mark.asyncio
async def test_get_all_messages(async_client: AsyncClient, clear_db):
    # Sign up and log in to get the token
    token = await sign_up_and_login(async_client, "testchat@example.com", "password123")

    # Create a new chat room to get its ID
    chat_room_data = ChatRoomCreateSchema(name="Test Room", members=[])
    create_response = await async_client.post(
        "/chat/chat_rooms/",
        json=chat_room_data.model_dump(),  # Use model_dump()
        headers={"Authorization": f"Bearer {token}"}
    )
    chat_room_id = create_response.json()["id"]

    # Create a new message
    message_data = MessageCreateSchema(
        sender="testchat@example.com",
        content="Hello, world!",
        timestamp="2024-08-13T00:00:00Z"
    )
    await async_client.post(
        f"/chat/chat_rooms/{chat_room_id}/messages",
        json=message_data.model_dump(),  # Use model_dump()
        headers={"Authorization": f"Bearer {token}"}
    )

    # Get all messages in the chat room
    response = await async_client.get(
        f"/chat/chat_rooms/{chat_room_id}/messages",
        headers={"Authorization": f"Bearer {token}"}
    )

    # Check if the response status is 200 OK
    assert response.status_code == 200

    # Verify the response data
    response_data = response.json()
    assert len(response_data) > 0
    assert response_data[0]["content"] == "Hello, world!"
