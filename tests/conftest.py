import asyncio
import os

import pytest
import socketio
from dotenv import load_dotenv
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.database import get_database
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
async def socket_client():
    client = socketio.AsyncClient()
    await client.connect('http://localhost:8000/ws', headers={'Authorization': 'Bearer YOUR_TEST_TOKEN'})
    yield client
    await client.disconnect()
