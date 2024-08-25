Read this in other
languages: <a href="https://github.com/Pooria82/Chat-Service/blob/main/Documents/Persian/b)%20Post-Service%20Implementation.fa.md">
Persian</a>
### Post-Service Implementation Documentation

#### Introduction

This document serves as a guide for front-end developers on how to use the chat service API. It provides detailed
instructions on interacting with the API endpoints for authentication, managing private and group chats, sending
messages, and uploading media files.

#### 1. Authentication

1. **User Signup:**
    - **API Endpoint:** `POST /auth/signup`
    - **Input:** User details including `username`, `email`, and `password`.
    - **Output:** Details of the newly registered user.

2. **User Login:**
    - **API Endpoint:** `POST /auth/login` or `POST /auth/token`
    - **Input:** Login credentials including `email` and `password`.
    - **Output:** JWT token for user authentication.

3. **Get Current User Information:**
    - **API Endpoint:** `GET /auth/users/me`
    - **Input:** JWT token in the Authorization header.
    - **Output:** Information of the currently authenticated user.

#### 2. Chat Management

1. **Get Private Chats:**
    - **API Endpoint:** `GET /chat/private_chats/`
    - **Input:** JWT token in the Authorization header.
    - **Output:** List of private chats with the online status of participants.

2. **Create a New Chat Room:**
    - **API Endpoint:** `POST /chat/chat_rooms/`
    - **Input:** Chat room details including `name` and `members`.
    - **Output:** Details of the newly created chat room.

3. **Get Messages in a Chat Room:**
    - **API Endpoint:** `GET /chat/chat_rooms/{room_id}/messages`
    - **Input:** Chat room ID.
    - **Output:** List of messages in the chat room.

4. **Send a Message to a Chat Room:**
    - **API Endpoint:** `POST /chat/chat_rooms/{room_id}/messages`
    - **Input:** Message content.
    - **Output:** Details of the sent message.

#### 3. Media File Upload

1. **Upload a File:**
    - **API Endpoint:** `POST /chat/upload_media/`
    - **Input:** File along with the JWT token.
    - **Output:** URL of the uploaded file.

#### 4. WebSocket (Socket.IO) Events

1. **Connect to Socket.IO Server:**
    - **URL:** `ws://localhost:8000/socket.io/`
    - **Input:** JWT token for authentication.
    - **Output:** Connection confirmation.

2. **Send a Message to a Chat Room:**
    - **Event:** `chat_message`
    - **Input:** Chat room ID and message content.
    - **Output:** Message sent confirmation.

3. **Receive New Messages:**
    - **Event:** `chat_response`
    - **Input:** None.
    - **Output:** New messages sent to the chat room.

4. **Get Online Users:**
    - **Event:** `get_online_users`
    - **Input:** None.
    - **Output:** List of online users in the chat room.

#### 5. Security Considerations

* **JWT Usage:** All requests must include an Authorization header with the value `Bearer <JWT>`.

* **User Status Management:** Ensure that user online statuses are managed and updated appropriately.

* **File Upload Restrictions:** Check that file sizes and types comply with server-defined limits to prevent security
  issues.

### Conclusion

These documents will help you understand how to implement and interact with the chat service. The first part (
pre-service) details the technical implementation and features, while the second part (post-service) provides
instructions for using the available APIs. With these guidelines, front-end developers and other team members can
effectively integrate and utilize the chat service in their applications.