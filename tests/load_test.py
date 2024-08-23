from locust import HttpUser, TaskSet, task, between


class ChatRoomTasks(TaskSet):
    def __init__(self, parent):
        super().__init__(parent)
        self.token = None
        self.headers = None
        self.room_id = None

    def on_start(self):
        # Simulate user login and store the access token
        response = self.client.post("/auth/login", data={
            "username": "testuser@example.com",
            "password": "testpassword"
        })

        print("Response status code:", response.status_code)
        print("Response content:", response.text)

        if response.status_code == 200:
            self.token = response.json().get("access_token")
            # Set the authorization header for subsequent requests
            self.headers = {
                "Authorization": f"Bearer {self.token}"
            }
        else:
            print("Login failed")

        # Create a chat room for testing
        response = self.client.post("/chat/chat_rooms/", json={
            "name": "Load Test Room",
            "members": ["loadtest@example.com"]
        }, headers=self.headers)
        self.room_id = response.json().get("id")

    @task
    def create_chat_room(self):
        # Create another chat room to test the API endpoint
        self.client.post("/chat/chat_rooms/", json={
            "name": "Load Test Room",
            "members": ["loadtest@example.com"]
        }, headers=self.headers)

    @task
    def send_message(self):
        # Send a message to the previously created chat room
        if self.room_id:
            self.client.post(f"/chat/chat_rooms/{self.room_id}/messages", json={
                "content": "This is a load test message"
            }, headers=self.headers)

    @task
    def get_all_messages(self):
        # Retrieve all messages from the chat room
        if self.room_id:
            self.client.get(f"/chat/chat_rooms/{self.room_id}/messages", headers=self.headers)


class LoadTestUser(HttpUser):
    wait_time = between(1, 5)

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.headers = None
        self.token = None

    def on_start(self):
        self.login()

    def login(self):
        response = self.client.post("/auth/login", data={"username": "your_email", "password": "your_password"})
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {
                "Authorization": f"Bearer {self.token}"
            }
        else:
            print("Login failed", response.text)

    @task
    def test_protected_endpoint(self):
        response = self.client.get("/chat/chat_rooms/", headers=self.headers)
        print(response.status_code, response.text)
