import pytest

from app.services.user_status_service import UserStatusService


@pytest.fixture
def user_status_service():
    return UserStatusService()


def test_set_user_online(user_status_service):
    user_status_service.set_user_online("user1", "sid1")
    assert "user1" in user_status_service.online_users


def test_set_user_offline(user_status_service):
    user_status_service.set_user_online("user1", "sid1")
    user_status_service.set_user_offline("user1", "sid1")
    assert "user1" not in user_status_service.online_users


def test_get_online_users(user_status_service):
    user_status_service.set_user_online("user1", "sid1")
    user_status_service.set_user_online("user2", "sid2")
    online_users = user_status_service.online_users
    assert len(online_users) == 2


def test_get_room_online_users(user_status_service):
    # Simulate a room by using the same room key for multiple users
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
