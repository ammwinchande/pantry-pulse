"""
JWT Credential Adapter — password hashing (PBKDF2) and token issuance/verification.

Implements CredentialPort. Stateless and thread-safe.
"""
import hashlib
import hmac
import secrets
import time
from typing import Optional

import jwt

from src.config import settings
from src.domain.models import UserRole
from src.ports.driven.credential_port import CredentialPort

# PBKDF2 parameters (OWASP-recommended minimums)
_PBKDF2_ITERATIONS = 210_000
_HASH_ALGO = "sha256"
_SALT_BYTES = 16


class JWTCredentialAdapter(CredentialPort):
    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: Optional[str] = None,
    ):
        self._secret = secret_key or settings.jwt_secret_key
        self._algorithm = algorithm or settings.jwt_algorithm
        if self._secret in ("", "dev-only-secret-change-me-0123456789abcdef") and settings.environment == "production":
            raise ValueError(
                "JWT_SECRET_KEY must be set to a strong value in production."
            )

    # --- Password hashing (PBKDF2-HMAC-SHA256, per-user salt) ---
    def hash_password(self, password: str) -> str:
        salt = secrets.token_bytes(_SALT_BYTES)
        digest = hashlib.pbkdf2_hmac(
            _HASH_ALGO, password.encode("utf-8"), salt, _PBKDF2_ITERATIONS
        )
        # Format: pbkdf2$<iterations>$<salt_hex>$<digest_hex>
        return f"pbkdf2${_PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"

    def verify_password(self, password: str, password_hash: str) -> bool:
        try:
            scheme, iterations, salt_hex, digest_hex = password_hash.split("$")
            if scheme != "pbkdf2":
                return False
            salt = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(digest_hex)
            candidate = hashlib.pbkdf2_hmac(
                _HASH_ALGO, password.encode("utf-8"), salt, int(iterations)
            )
            return hmac.compare_digest(candidate, expected)
        except (ValueError, AttributeError):
            return False

    # --- Access tokens (JWT) ---
    def create_access_token(
        self, user_id: str, email: str, role: str, expires_in_seconds: int
    ) -> str:
        now = int(time.time())
        payload = {
            "sub": user_id,
            "email": email,
            "role": role,
            "type": "access",
            "iat": now,
            "exp": now + expires_in_seconds,
            "jti": secrets.token_hex(8),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode_access_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        if payload.get("type") != "access":
            return None
        return payload

    # --- Single-purpose email tokens (verification / reset) ---
    def create_email_token(self, user_id: str, purpose: str, expires_in_seconds: int) -> str:
        now = int(time.time())
        payload = {
            "sub": user_id,
            "purpose": purpose,
            "type": "email",
            "iat": now,
            "exp": now + expires_in_seconds,
            "jti": secrets.token_hex(8),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode_email_token(self, token: str, purpose: str) -> Optional[str]:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        if payload.get("type") != "email" or payload.get("purpose") != purpose:
            return None
        return payload.get("sub")
