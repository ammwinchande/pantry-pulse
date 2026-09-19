"""
AuthService — application service implementing the AuthUseCase.

Orchestrates the user repository, credential (JWT) port, and email port
to handle registration, email verification, login, and password
reset/change flows.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from src.config import settings
from src.domain.exceptions import (
    AuthenticationError,
    EmailAlreadyRegisteredError,
    InvalidTokenError,
    UserNotFoundError,
)
from src.domain.models import AuthToken, User, UserRole
from src.ports.driven.credential_port import CredentialPort
from src.ports.driven.email_port import EmailPort
from src.ports.driven.user_repo_port import UserRepositoryPort
from src.ports.driving.auth_use_case import AuthUseCase

logger = logging.getLogger("PantryPulseAuth")

MIN_PASSWORD_LENGTH = 8


class AuthService(AuthUseCase):
    def __init__(
        self,
        user_repo: UserRepositoryPort,
        credentials: CredentialPort,
        email: EmailPort,
    ):
        self._users = user_repo
        self._credentials = credentials
        self._email = email

    # --- Registration & activation ---
    def register(self, name: str, email: str, password: str, role: UserRole) -> User:
        email = email.strip().lower()
        if not name or not name.strip():
            raise AuthenticationError("A display name is required.")
        if not email or "@" not in email:
            raise AuthenticationError("A valid email address is required.")
        self._enforce_password_policy(password)

        if self._users.get_by_email(email):
            raise EmailAlreadyRegisteredError(email)

        user = User(
            name=name.strip(),
            email=email,
            role=role,
            is_active=False,
            password_hash=self._credentials.hash_password(password),
        )
        self._users.save(user)

        token = self._credentials.create_email_token(
            user.id, "email_verification",
            settings.email_verification_token_expire_minutes * 60,
        )
        self._email.send_activation_email(user.name, user.email, token)
        logger.info("Registered new %s user: %s", role.value, email)
        return user

    def verify_email(self, token: str) -> User:
        user_id = self._credentials.decode_email_token(token, "email_verification")
        if not user_id:
            raise InvalidTokenError("verification link is invalid or has expired")
        user = self._users.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        if user.is_active:
            return user  # idempotent
        user.is_active = True
        user.email_verified_at = datetime.now(timezone.utc)
        self._users.save(user)
        logger.info("Email verified for user %s", user.email)
        return user

    # --- Login ---
    def login(self, email: str, password: str) -> AuthToken:
        user = self._users.get_by_email(email.strip().lower())
        # Uniform error to prevent user enumeration
        if not user or not user.password_hash or not self._credentials.verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid email or password.")
        if not user.is_active:
            raise AuthenticationError("Account is not activated. Please check your email for the verification link.")
        expires = settings.access_token_expire_minutes * 60
        access_token = self._credentials.create_access_token(
            user.id, user.email, user.role.value, expires
        )
        return AuthToken(access_token=access_token, expires_in=expires, user=user)

    def get_profile(self, user_id: str) -> User:
        user = self._users.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        return user

    # --- Password reset ---
    def request_password_reset(self, email: str) -> None:
        user = self._users.get_by_email(email.strip().lower())
        # Always succeed silently to avoid user enumeration
        if not user:
            logger.info("Password reset requested for unknown email (no-op).")
            return
        token = self._credentials.create_email_token(
            user.id, "password_reset",
            settings.password_reset_token_expire_minutes * 60,
        )
        self._email.send_password_reset_email(user.name, user.email, token)
        logger.info("Password reset email sent to %s", user.email)

    def request_password_reset_token(self, email: str) -> Optional[str]:
        """Dev aid: mint and return a reset token for a known email.

        Returns None for unknown emails. Only used when expose_dev_tokens is
        enabled so judges can complete the reset flow without an inbox.
        """
        user = self._users.get_by_email(email.strip().lower())
        if not user:
            return None
        token = self._credentials.create_email_token(
            user.id, "password_reset",
            settings.password_reset_token_expire_minutes * 60,
        )
        self._email.send_password_reset_email(user.name, user.email, token)
        return token

    def reset_password(self, token: str, new_password: str) -> None:
        user_id = self._credentials.decode_email_token(token, "password_reset")
        if not user_id:
            raise InvalidTokenError("reset link is invalid or has expired")
        user = self._users.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        self._enforce_password_policy(new_password)
        user.password_hash = self._credentials.hash_password(new_password)
        self._users.save(user)
        self._email.send_password_changed_email(user.name, user.email)
        logger.info("Password reset completed for %s", user.email)

    # --- Password change (authenticated) ---
    def change_password(self, user_id: str, current_password: str, new_password: str) -> None:
        user = self._users.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        if not user.password_hash or not self._credentials.verify_password(current_password, user.password_hash):
            raise AuthenticationError("Current password is incorrect.")
        self._enforce_password_policy(new_password)
        user.password_hash = self._credentials.hash_password(new_password)
        self._users.save(user)
        self._email.send_password_changed_email(user.name, user.email)
        logger.info("Password changed for %s", user.email)

    # --- Helpers ---
    @staticmethod
    def _enforce_password_policy(password: str) -> None:
        if len(password) < MIN_PASSWORD_LENGTH:
            raise AuthenticationError(
                f"Password must be at least {MIN_PASSWORD_LENGTH} characters long."
            )
