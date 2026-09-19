"""
In-Memory User Repository — implements UserRepositoryPort.

Seeds a demo coordinator account so the application is usable immediately
after boot (password: "Coordinator123!"). In production this would be
replaced by a database-backed adapter implementing the same port.
"""
import threading
from typing import Dict, List, Optional

from src.domain.models import User, UserRole
from src.ports.driven.user_repo_port import UserRepositoryPort


class InMemoryUserRepository(UserRepositoryPort):
    def __init__(self):
        self._lock = threading.RLock()
        self._users: Dict[str, User] = {}
        self._email_index: Dict[str, str] = {}

    # --- UserRepositoryPort ---
    def save(self, user: User) -> User:
        with self._lock:
            if user.id in self._users:
                old_email = self._users[user.id].email
                if old_email != user.email:
                    self._email_index.pop(old_email, None)
            self._users[user.id] = user
            self._email_index[user.email] = user.id
            return user

    def get_by_id(self, user_id: str) -> Optional[User]:
        with self._lock:
            return self._users.get(user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        with self._lock:
            user_id = self._email_index.get(email)
            return self._users.get(user_id) if user_id else None

    def list_all(self) -> List[User]:
        with self._lock:
            return list(self._users.values())

    def list_by_role(self, role: UserRole) -> List[User]:
        with self._lock:
            return [u for u in self._users.values() if u.role == role]

    # --- Test helpers ---
    def reset(self) -> None:
        with self._lock:
            self._users.clear()
            self._email_index.clear()
