import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_send_message(async_client: AsyncClient, clear_db):
    # Sign up a new user
    response = await async_client.post("/auth/signup", json={
        "username": "testuser",
        "email": "testchat@example.com",
        "password": "password123"
    })
    assert response.status_code == 201

    # Log in the user
    response = await async_client.post("/auth/login", data={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Send a message
    response = await async_client.post("/chat/send", json={
        "message": "Hello, world!"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Hello, world!"
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_get_messages(async_client: AsyncClient, clear_db):
    # Sign up a new user
    response = await async_client.post("/auth/signup", json={
        "username": "testuser",
        "email": "testchat@example.com",
        "password": "password123"
    })
    assert response.status_code == 201

    # Log in the user
    response = await async_client.post("/auth/login", data={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Send a message
    response = await async_client.post("/chat/send", json={
        "message": "Hello, world!"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    # Fetch messages
    response = await async_client.get("/chat/messages", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()

    # Ensure the data is a list
    assert isinstance(data, list)

    # Ensure that there are messages
    assert len(data) > 0


# Additional tests
@pytest.mark.asyncio
async def test_no_messages(async_client: AsyncClient, clear_db):
    # Sign up a new user
    response = await async_client.post("/auth/signup", json={
        "username": "testuser",
        "email": "testchat@example.com",
        "password": "password123"
    })
    assert response.status_code == 201

    # Log in the user
    response = await async_client.post("/auth/login", data={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Fetch messages
    response = await async_client.get("/chat/messages", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()

    # Ensure the data is a list
    assert isinstance(data, list)
    assert len(data) == 0  # Expect no messages initially


@pytest.mark.asyncio
async def test_invalid_message(async_client: AsyncClient, clear_db):
    # Send an invalid message
    response = await async_client.post("/chat/send", json={
        "message": ""
    }, headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401  # Unauthorized or Bad Request
    data = response.json()
    assert "detail" in data
