# import warnings
import pytest
from fastapi.testclient import TestClient

from app.main import app


# warnings.filterwarnings('always')


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.mark.anyio
async def test_create_user(test_client: TestClient, clear_db):
    response = test_client.post("/auth/signup", json={
        "username": "testuser",
        "email": "testunique@example.com",
        "password": "password123"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testunique@example.com"


@pytest.mark.anyio
async def test_login_user(test_client: TestClient, clear_db):
    # First create the user
    response = test_client.post("/auth/signup", json={
        "username": "testuser",
        "email": "testlogin@example.com",
        "password": "password123"
    })
    assert response.status_code == 200

    # Then login
    response = test_client.post("/auth/login", data={
        "username": "testlogin@example.com",
        "password": "password123"
    })
    assert response.status_code == 200


@pytest.mark.anyio
async def test_get_current_user(test_client: TestClient, clear_db):
    # First create the user
    test_client.post("/auth/signup", json={
        "username": "testuser",
        "email": "testcurrent@example.com",
        "password": "password123"
    })

    # Then login
    login_response = test_client.post("/auth/login", data={
        "username": "testcurrent@example.com",
        "password": "password123"
    })
    assert login_response.status_code == 200
    login_data = login_response.json()
    token = login_data["access_token"]

    # Use the token to get the current user
    response = test_client.get("/auth/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testcurrent@example.com"
    assert "id" in data
