import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_integration_create_and_send_message(async_client: AsyncClient, get_auth_token):
    token = get_auth_token

    # Create a chat room
    response = await async_client.post("/chat/chat_rooms/", json={
        "name": "Integration Test Room",
        "members": ["integrationtest@example.com"]
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    room_id = response.json()["id"]

    # Send a message to the created chat room
    response = await async_client.post("/chat/send_message/", json={
        "room_id": room_id,
        "message": "Integration test message"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {'status': 'received', 'message': 'Integration test message'}
