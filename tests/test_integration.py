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
    room_id = response.json().get("id")
    assert room_id is not None, "Failed to retrieve chat room ID"

    # Send a message to the created chat room
    response = await async_client.post("/chat/chat_rooms/{room_id}/messages", json={
        "content": "Integration test message"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {'status': 'received', 'message': 'Integration test message'}

    response = await async_client.get(f"/chat/chat_rooms/{room_id}/messages",
                                      headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    messages = response.json()
    assert any(
        message["content"] == "Integration test message" for message in messages), "Message was not found in chat room"
