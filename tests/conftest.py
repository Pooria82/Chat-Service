import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.database import get_database
from app.main import app

# Load environment variables
load_dotenv()


# Fixture to provide a TestClient instance
@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client


# Fixture to set up the test database
@pytest.fixture(scope="module")
async def setup_db():
    db_url = os.getenv("DATABASE_URL")
    db_name = os.getenv("DATABASE_NAME")
    test_database = AsyncIOMotorClient(db_url)
    db = test_database[db_name]

    # Override the dependency to use the test database
    app.dependency_overrides[get_database] = lambda: db

    yield db

    # Close the database connection after tests
    test_database.close()


# Fixture to clear the database before each test
@pytest.fixture(scope="function")
async def clear_db(setup_db):
    db = setup_db
    # Clear all collections in the test database
    for collection_name in await db.list_collection_names():
        await db[collection_name].delete_many({})

    yield
