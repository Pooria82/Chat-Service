Read this in other languages: <a href="https://github.com/Pooria82/Chat-Service/blob/main/README.fa.md">Persian</a>

# Chat Service

## Overview

The Chat Service is a FastAPI-based application that provides real-time chat functionality with user authentication,
private chats, chat rooms, and media file uploads. It also includes WebSocket (Socket.IO) support for live messaging.

## Features

- **User Authentication:** Register and log in users with secure JWT-based authentication.
- **Private Chats:** Chat privately with other users, with online status tracking.
- **Chat Rooms:** Create and manage group chat rooms.
- **Media Uploads:** Upload media files to be shared within chat rooms.
- **Real-Time Messaging:** Utilize Socket.IO for real-time messaging with online status tracking.

## Prerequisites

- **Docker:** Ensure you have Docker and Docker Compose installed on your machine.
- **Python 3.8+** (if running locally without Docker)

## Running the Service

### Using Docker (Recommended)

The easiest way to run the service is by using Docker. This method ensures all dependencies and configurations are
handled automatically.

#### Steps:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Pooria82/Chat-Service.git
   cd Chat-Service
   ```

2. **Build and Run the Containers:**
    - **For Linux/MacOS:**
      ```bash
      docker-compose up --build
      ```
    - **For Windows:**
      ```bash
      docker-compose -f docker-compose.yml up --build
      ```

3. **Access the Service:**
    - The service will be available at `http://localhost:8000`.
    - You can access the interactive API documentation at `http://localhost:8000/docs`.

### Running Locally (Without Docker)

If you prefer to run the service directly on your machine:

#### Steps:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Pooria82/Chat-Service.git
   cd Chat-Service
   ```

2. **Create and Activate a Virtual Environment:**
    - **For Linux/MacOS:**
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```
    - **For Windows:**
      ```bash
      python -m venv venv
      venv\Scripts\activate
      ```

3. **Install the Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables:**
   Create a `.env` file in the project root with the necessary environment variables. Example:
   ```
   SECRET_KEY=your_secret_key
   DATABASE_URL=mongodb://localhost:27017/chat_db
   ```

5. **Run the Application:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

6. **Access the Service:**
    - The service will be available at `http://localhost:8000`.
    - You can access the interactive API documentation at `http://localhost:8000/docs`.

## Using the APIs

### Authentication

- **Sign Up:**
    - **Endpoint:** `POST /auth/signup`
    - **Request Body:**
      ```json
      {
        "username": "string",
        "email": "string",
        "password": "string"
      }
      ```
    - **Response:** Returns the newly created user's details.

- **Login:**
    - **Endpoint:** `POST /auth/login` or `POST /auth/token`
    - **Request Form Data:**
        - `username`: The user's email.
        - `password`: The user's password.
    - **Response:**
      ```json
      {
        "access_token": "string",
        "token_type": "bearer"
      }
      ```

- **Get Current User:**
    - **Endpoint:** `GET /auth/users/me`
    - **Response:** Returns the authenticated user's details.

### Private Chats

- **Get Private Chats:**
    - **Endpoint:** `GET /chat/private_chats/`
    - **Response:** Returns a list of private chats with the online status of participants.

### Chat Rooms

- **Create New Chat Room:**
    - **Endpoint:** `POST /chat/chat_rooms/`
    - **Request Body:**
      ```json
      {
        "name": "string",
        "description": "string",
        "members": ["string"]
      }
      ```
    - **Response:** Returns the details of the newly created chat room.

- **Get Chat Room Details:**
    - **Endpoint:** `GET /chat/chat_rooms/{room_id}`
    - **Response:** Returns the chat room's details.

- **Send Message:**
    - **Endpoint:** `POST /chat/chat_rooms/{room_id}/messages`
    - **Request Body:**
      ```json
      {
        "content": "string"
      }
      ```
    - **Response:** Returns the details of the sent message.

- **Get All Messages:**
    - **Endpoint:** `GET /chat/chat_rooms/{room_id}/messages`
    - **Response:** Returns a list of messages in the chat room.

### Media Uploads

- **Upload Media:**
    - **Endpoint:** `POST /chat/upload_media/`
    - **Request:** Multipart/form-data with the file to upload.
    - **Response:** Returns the URL of the uploaded media file.

### WebSocket (Socket.IO) Events

- **Connect:** Establishes a WebSocket connection with the server. Requires a valid JWT token.
- **Disconnect:** Handles user disconnection, marking the user as offline.
- **Send Message:** Broadcasts a chat message to a room.
- **Get Online Users:** Retrieves the list of currently online users.

## Technical Details

- **Backend:** FastAPI
- **Database:** MongoDB
- **WebSocket:** Socket.IO
- **Authentication:** JWT (JSON Web Tokens)
- **Media Storage:** Local storage (can be configured for cloud storage)
- **Environment:** Configurable via `.env` file

## License

This project is licensed under the MIT License.