import pytest
from starlette.testclient import TestClient

from app.main import app


@pytest.mark.asyncio
async def test_websocket_connection():
    client = TestClient(app)
    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json({"message": "Hello, WebSocket!"})
        data = websocket.receive_json()
        assert data["message"] == "Hello, WebSocket!"


@pytest.mark.asyncio
async def test_websocket_broadcast():
    client = TestClient(app)
    with client.websocket_connect("/ws/chat") as websocket1:
        with client.websocket_connect("/ws/chat") as websocket2:
            websocket1.send_json({"message": "Broadcasting message"})
            data1 = websocket1.receive_json()
            data2 = websocket2.receive_json()
            assert data1["message"] == "Broadcasting message"
            assert data2["message"] == "Broadcasting message"
