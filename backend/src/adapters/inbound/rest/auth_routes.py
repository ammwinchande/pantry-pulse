"""
Inbound REST routes for authentication & account management.

Mounted under /api/auth via the create_auth_router factory (matching the
business router pattern). Business routes in routes.py are protected with
the get_current_user / require_role dependencies from auth.py.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from src.config import settings
from src.domain.exceptions import (
    AuthenticationError,
    EmailAlreadyRegisteredError,
    InvalidTokenError,
    UserNotFoundError,
)
from src.domain.models import User, UserRole
from src.ports.driving.auth_use_case import AuthUseCase
from src.ports.driven.credential_port import CredentialPort
from src.ports.driven.email_port import EmailPort
from src.adapters.inbound.rest.auth import get_current_user


# --- Request / response schemas ---
class UserResponse(BaseModel):
    """Public user shape. Deliberately omits password_hash."""
    id: str
    name: str
    email: str
    role: UserRole
    organization: str
    is_active: bool
    email_verified_at: Optional[datetime] = None
    created_at: datetime


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.VOLUNTEER


class RegisterResponse(BaseModel):
    user: UserResponse
    message: str
    activation_url: Optional[str] = None


class VerifyEmailRequest(BaseModel):
    token: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class MessageResponse(BaseModel):
    message: str
    reset_url: Optional[str] = None


def _user_response(user: User) -> UserResponse:
    """Project a domain User onto the public response shape (drops password_hash)."""
    return UserResponse.model_validate(user.model_dump())


def create_auth_router(
    auth_service: AuthUseCase,
    credential_port: CredentialPort,
    email_adapter: EmailPort,
) -> APIRouter:
    router = APIRouter(prefix="/auth", tags=["auth"])

    @router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
    def register(body: RegisterRequest):
        try:
            user = auth_service.register(body.name, body.email, body.password, body.role)
        except EmailAlreadyRegisteredError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        except AuthenticationError as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

        activation_url = None
        if settings.expose_dev_tokens:
            # Dev aid: mint a fresh verification token so the flow can be
            # completed without an inbox. NOT returned in production.
            token = credential_port.create_email_token(
                user.id, "email_verification",
                settings.email_verification_token_expire_minutes * 60,
            )
            activation_url = email_adapter.activation_link(token)

        return RegisterResponse(
            user=_user_response(user),
            message="Account created. Check your email to activate it.",
            activation_url=activation_url,
        )

    @router.post("/verify-email", response_model=UserResponse)
    def verify_email(body: VerifyEmailRequest):
        try:
            return _user_response(auth_service.verify_email(body.token))
        except InvalidTokenError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except UserNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    @router.post("/login", response_model=LoginResponse)
    def login(body: LoginRequest):
        try:
            token = auth_service.login(body.email, body.password)
        except AuthenticationError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
        return LoginResponse(
            access_token=token.access_token,
            token_type=token.token_type,
            expires_in=token.expires_in,
            user=_user_response(token.user),
        )

    @router.get("/me", response_model=UserResponse)
    def me(current_user: User = Depends(get_current_user)):
        return _user_response(current_user)

    @router.post("/password-reset/request", response_model=MessageResponse)
    def password_reset_request(body: PasswordResetRequest):
        reset_url = None
        if settings.expose_dev_tokens:
            # Dev aid: mint a reset token so the flow can be completed
            # without an inbox. Returns None for unknown emails.
            token = auth_service.request_password_reset_token(body.email)
            if token:
                reset_url = email_adapter.reset_link(token)
        else:
            auth_service.request_password_reset(body.email)
        # Uniform message regardless of whether the email exists.
        return MessageResponse(
            message="If that address is registered, a reset link has been sent.",
            reset_url=reset_url,
        )

    @router.post("/password-reset/confirm", response_model=MessageResponse)
    def password_reset_confirm(body: PasswordResetConfirmRequest):
        try:
            auth_service.reset_password(body.token, body.new_password)
        except InvalidTokenError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except UserNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except AuthenticationError as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
        return MessageResponse(message="Password updated. You can now sign in.")

    @router.post("/password-change", response_model=MessageResponse)
    def password_change(
        body: PasswordChangeRequest,
        current_user: User = Depends(get_current_user),
    ):
        try:
            auth_service.change_password(current_user.id, body.current_password, body.new_password)
        except AuthenticationError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
        return MessageResponse(message="Password changed successfully.")

    return router
