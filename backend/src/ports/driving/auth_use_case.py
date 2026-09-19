from abc import ABC, abstractmethod
from typing import Optional

from src.domain.models import User, AuthToken, UserRole


class AuthUseCase(ABC):
    """Inbound port for authentication & account management."""

    @abstractmethod
    def register(self, name: str, email: str, password: str, role: UserRole) -> User:
        """
        Create a new user account with an inactive status and issue an
        email-verification token delivered via EmailPort.
        """
        pass

    @abstractmethod
    def verify_email(self, token: str) -> User:
        """Activate an account using the emailed verification token."""
        pass

    @abstractmethod
    def login(self, email: str, password: str) -> AuthToken:
        """Authenticate and return a signed JWT access token."""
        pass

    @abstractmethod
    def get_profile(self, user_id: str) -> User:
        """Return the authenticated user's profile."""
        pass

    @abstractmethod
    def request_password_reset(self, email: str) -> None:
        """
        Issue a password-reset token and email the reset link.
        Always returns None (no user enumeration).
        """
        pass

    @abstractmethod
    def reset_password(self, token: str, new_password: str) -> None:
        """Set a new password using a valid reset token, then notify the user."""
        pass

    @abstractmethod
    def change_password(self, user_id: str, current_password: str, new_password: str) -> None:
        """Change password for an authenticated user, then notify the user."""
        pass
