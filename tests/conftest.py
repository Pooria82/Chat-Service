import asyncio
import os
import uuid

import pytest
import socketio
from dotenv import load_dotenv
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.database import get_database
from app.dependencies import get_db
from app.main import app

# Load environment variables
load_dotenv()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_db():
    db_url = os.getenv("DATABASE_URL")
    db_name = os.getenv("DATABASE_NAME")
    client = AsyncIOMotorClient(db_url)
    db = client[db_name]

    # Override the dependency to use the test database
    app.dependency_overrides[get_database] = lambda: db

    yield db

    # Close the database connection after tests
    client.close()


@pytest.fixture(scope="function")
async def clear_db(setup_db):
    db = setup_db
    for collection_name in await db.list_collection_names():
        await db[collection_name].delete_many({})
    yield db


@pytest.fixture(scope="function")
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="function")
async def get_auth_token(async_client):
    # Sign up a new user with a random email
    random_email = f"testuser_{uuid.uuid4()}@example.com"
    signup_data = {
        "username": "testuser",
        "email": random_email,
        "password": "password123"
    }
    response = await async_client.post("/auth/signup", json=signup_data)
    if response.status_code != 201:
        print("Signup request data:", signup_data)
        print("Signup response status code:", response.status_code)
        print("Signup response content:", response.content)
        try:
            print("Signup response json:", response.json())
        except Exception as e:
            print("Error parsing signup response json:", e)
    assert response.status_code == 201

    # Log in the user
    login_data = {
        "username": random_email,
        "password": "password123"
    }
    response = await async_client.post("/auth/login", data=login_data)
    if response.status_code != 200:
        print("Login request data:", login_data)
        print("Login response status code:", response.status_code)
        print("Login response content:", response.content)
        try:
            print("Login response json:", response.json())
        except Exception as e:
            print("Error parsing login response json:", e)
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="function")
async def socket_client(get_auth_token, setup_db):
    client = socketio.AsyncClient()

    app.dependency_overrides[get_db] = lambda: setup_db

    await client.connect('http://localhost:8000/ws/socket.io', headers={'Authorization': f'Bearer {get_auth_token}'})
    yield client
    await client.disconnect()
