from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.models import User, UserRole


class UserRepositoryPort(ABC):
    """Outbound SPI for persisting application users."""

    @abstractmethod
    def save(self, user: User) -> User:
        """Create or update a user."""
        pass

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def list_all(self) -> List[User]:
        pass

    @abstractmethod
    def list_by_role(self, role: UserRole) -> List[User]:
        pass
