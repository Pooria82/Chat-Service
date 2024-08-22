from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models import UserInDB
from app.services.chat_service import ChatService
from app.services.user_status_service import UserStatusService


@pytest.fixture
def user_status_service():
    return UserStatusService()


@pytest.fixture
def chat_service(user_status_service):
    # Mock database collection
    db_chat_rooms_mock = AsyncMock()

    # Mock the `find` method to return another mock with `to_list` method
    to_list_mock = AsyncMock(return_value=[
        {"_id": "chat1", "members": ["user1_id", "user2_id"], "is_group_chat": False},
        {"_id": "chat2", "members": ["user1_id", "user3_id"], "is_group_chat": False}
    ])

    find_mock = AsyncMock(return_value=MagicMock(to_list=to_list_mock))

    db_chat_rooms_mock.find = find_mock

    return ChatService(
        db_chat_rooms=db_chat_rooms_mock,
        connection_manager=AsyncMock(),
        user_status_service=user_status_service
    )


@pytest.fixture
def current_user():
    return UserInDB(
        email="user1@example.com",
        id="user1_id",
        username="user1",
        hashed_password="hashed_password_example"
    )


@pytest.mark.asyncio
async def test_set_user_online(user_status_service):
    user_status_service.set_user_online("user1", "sid1")
    assert "user1" in user_status_service.online_users


@pytest.mark.asyncio
async def test_set_user_offline(user_status_service):
    user_status_service.set_user_online("user1", "sid1")
    user_status_service.set_user_offline("user1", "sid1")
    assert "user1" not in user_status_service.online_users


@pytest.mark.asyncio
async def test_get_online_users(user_status_service):
    user_status_service.set_user_online("user1", "sid1")
    user_status_service.set_user_online("user2", "sid2")
    online_users = user_status_service.online_users
    assert len(online_users) == 2


@pytest.mark.asyncio
async def test_get_room_online_users(user_status_service):
    user_status_service.set_user_online("room1", "sid1")
    user_status_service.set_user_online("room1", "sid2")
    user_status_service.set_user_online("room2", "sid3")

    room1_users = user_status_service.get_room_online_users("room1")
    assert len(room1_users) == 2
    assert "sid1" in room1_users
    assert "sid2" in room1_users

    room2_users = user_status_service.get_room_online_users("room2")
    assert len(room2_users) == 1
    assert "sid3" in room2_users
