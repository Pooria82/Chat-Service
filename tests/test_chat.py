import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_send_message(client: AsyncClient):
    # ثبت نام کاربر
    response = await client.post("/auth/signup", json={
        "username": "testuser",
        "email": "testchat@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
    # ورود کاربر
    response = await client.post("/auth/login", data={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]

    # ارسال پیام
    response = await client.post("/chat/send", json={
        "message": "Hello, world!"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Hello, world!"
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_get_messages(client: AsyncClient):
    response = await client.get("/chat/messages")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # فرض بر این است که پیام‌های ارسال شده در تست قبلی وجود دارند
    assert len(data) > 0
