from locust import HttpUser, TaskSet, task, between


class ChatRoomTasks(TaskSet):
    @task
    def create_chat_room(self):
        self.client.post("/chat/chat_rooms/", json={
            "name": "Load Test Room",
            "members": ["loadtest@example.com"]
        })

    @task
    def send_message(self):
        self.client.post("/chat/send_message/", json={
            "room_id": "load_test_room_id",
            "message": "This is a load test message"
        })


class LoadTestUser(HttpUser):
    tasks = [ChatRoomTasks]
    wait_time = between(1, 5)  # Simulate user wait time between tasks

    def on_start(self):
        # Simulate user login
        self.client.post("/auth/login", json={
            "email": "testuser@example.com",
            "password": "testpassword"
        })
