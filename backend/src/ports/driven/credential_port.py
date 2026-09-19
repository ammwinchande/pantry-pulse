from abc import ABC, abstractmethod
from typing import Optional


class CredentialPort(ABC):
    """
    Outbound SPI for password hashing and JWT issuance/verification.

    Implementations must be stateless and safe to share across threads.
    """

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Return a salted hash of the plaintext password."""
        pass

    @abstractmethod
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Constant-time comparison of a plaintext password against its hash."""
        pass

    @abstractmethod
    def create_access_token(self, user_id: str, email: str, role: str, expires_in_seconds: int) -> str:
        """Issue a signed JWT access token for an authenticated user."""
        pass

    @abstractmethod
    def decode_access_token(self, token: str) -> Optional[dict]:
        """
        Verify signature + expiry and return the token claims,
        or None if the token is invalid/expired.
        """
        pass

    @abstractmethod
    def create_email_token(self, user_id: str, purpose: str, expires_in_seconds: int) -> str:
        """
        Issue a single-purpose signed token (email verification / password reset).
        `purpose` is one of: "email_verification" | "password_reset".
        """
        pass

    @abstractmethod
    def decode_email_token(self, token: str, purpose: str) -> Optional[str]:
        """
        Verify a single-purpose token and return the user_id it was issued for,
        or None if invalid/expired/purpose mismatch.
        """
        pass
