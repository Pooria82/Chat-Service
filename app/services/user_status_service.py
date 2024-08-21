from typing import Dict, Set

from app.services.connection_manager import connection_manager


class UserStatusService:
    def __init__(self):
        self.active_connections: Dict[str, Set[str]] = {}

    def set_user_online(self, email: str, sid: str):
        if email not in self.active_connections:
            self.active_connections[email] = set()
        self.active_connections[email].add(sid)
        print(f"[LOG] User {email} connected with SID {sid}. Active connections: {self.active_connections}")

    def set_user_offline(self, email: str, sid: str):
        if email in self.active_connections:
            self.active_connections[email].remove(sid)
            if not self.active_connections[email]:
                del self.active_connections[email]
            print(f"[LOG] User {email} disconnected with SID {sid}. Remaining connections: {self.active_connections}")

    @property
    def online_users(self) -> Set[str]:
        return set(self.active_connections.keys())

    def get_room_online_users(self, room: str) -> Set[str]:
        # Assuming that room corresponds to a key in the active_connections dict
        return set(self.active_connections.get(room, set()))

    async def broadcast(self, message: str, room: str = None):
        if room:
            targets = [sid for sid in self.active_connections.get(room, set())]
        else:
            targets = [sid for sids in self.active_connections.values() for sid in sids]

        for sid in targets:
            await connection_manager.send(sid, message)

    @staticmethod
    async def send_personal_message(message: str, sid: str):
        await connection_manager.send(sid, message)
