"""
Mailtrap Email Adapter — transactional email delivery via the Mailtrap API.

Implements EmailPort. Used for registration activation, password reset,
and password change notifications.

Configuration (see backend/.env.example):
    MAILTRAP_API_KEY        — Mailtrap sandbox API key
    MAILTRAP_SENDER_EMAIL   — verified sender address
    MAILTRAP_SENDER_NAME    — display name
    APP_BASE_URL            — frontend base URL for activation/reset links

If MAILTRAP_API_KEY is empty, the adapter degrades to a log-only mode so
local development and tests still work without network access.
"""
import logging
from typing import Optional

import httpx

from src.config import settings
from src.ports.driven.email_port import EmailPort

logger = logging.getLogger("PantryPulseEmail")

_MAILTRAP_API = "https://api.mailtrap.io/api/v1/send"


class MailtrapEmailAdapter(EmailPort):
    def __init__(
        self,
        api_key: Optional[str] = None,
        sender_email: Optional[str] = None,
        sender_name: Optional[str] = None,
        app_base_url: Optional[str] = None,
    ):
        self._api_key = api_key if api_key is not None else settings.mailtrap_api_key
        self._sender_email = sender_email or settings.mailtrap_sender_email
        self._sender_name = sender_name or settings.mailtrap_sender_name
        self._app_base_url = (app_base_url or settings.app_base_url).rstrip("/")
        self._enabled = bool(self._api_key)
        if not self._enabled:
            logger.warning(
                "MAILTRAP_API_KEY not set — email delivery disabled (log-only mode)."
            )

    # --- Public helpers for building message links ---
    def activation_link(self, token: str) -> str:
        return f"{self._app_base_url}/activate?token={token}"

    def reset_link(self, token: str) -> str:
        return f"{self._app_base_url}/reset-password?token={token}"

    # --- EmailPort ---
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str = "",
    ) -> bool:
        if not self._enabled:
            logger.info(
                "[EMAIL:log-only] to=%s subject=%r\n%s", to_email, subject, text_body or html_body
            )
            return True

        payload = {
            "from": {"email": self._sender_email, "name": self._sender_name},
            "to": [{"email": to_email}],
            "subject": subject,
            "text": text_body or "Please see the HTML version of this message.",
            "html": html_body,
        }
        try:
            resp = httpx.post(
                _MAILTRAP_API,
                headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=15.0,
            )
            if resp.status_code in (200, 201):
                logger.info("[EMAIL:mailtrap] delivered to=%s subject=%r", to_email, subject)
                return True
            logger.error(
                "[EMAIL:mailtrap] failed status=%s body=%s to=%s",
                resp.status_code, resp.text[:300], to_email,
            )
            return False
        except httpx.HTTPError as exc:
            logger.error("[EMAIL:mailtrap] transport error: %s", exc)
            return False

    # --- Message templates ---
    def send_activation_email(self, user_name: str, user_email: str, token: str) -> bool:
        link = self.activation_link(token)
        subject = "Confirm your PantryPulse account"
        html = f"""
        <div style="font-family:Arial,Helvetica,sans-serif;max-width:560px;margin:auto;">
          <h2 style="color:#059669;">Welcome to PantryPulse, {user_name}!</h2>
          <p>Thanks for registering. Please confirm your email address to activate your account:</p>
          <p><a href="{link}" style="background:#059669;color:#fff;padding:12px 20px;
             border-radius:8px;text-decoration:none;display:inline-block;">Activate my account</a></p>
          <p style="color:#64748b;font-size:13px;">Or paste this link into your browser:<br>{link}</p>
          <p style="color:#64748b;font-size:13px;">This link expires in
             {settings.email_verification_token_expire_minutes} minutes. If you didn't create an
             account, you can ignore this email.</p>
        </div>
        """
        text = (
            f"Welcome to PantryPulse, {user_name}!\n\n"
            f"Confirm your email to activate your account:\n{link}\n\n"
            f"This link expires in {settings.email_verification_token_expire_minutes} minutes."
        )
        return self.send_email(user_email, subject, html, text)

    def send_password_reset_email(self, user_name: str, user_email: str, token: str) -> bool:
        link = self.reset_link(token)
        subject = "Reset your PantryPulse password"
        html = f"""
        <div style="font-family:Arial,Helvetica,sans-serif;max-width:560px;margin:auto;">
          <h2 style="color:#059669;">Password reset requested</h2>
          <p>Hi {user_name},</p>
          <p>We received a request to reset the password for your PantryPulse account.
             Click the button below to choose a new password:</p>
          <p><a href="{link}" style="background:#059669;color:#fff;padding:12px 20px;
             border-radius:8px;text-decoration:none;display:inline-block;">Reset my password</a></p>
          <p style="color:#64748b;font-size:13px;">Or paste this link into your browser:<br>{link}</p>
          <p style="color:#64748b;font-size:13px;">This link expires in
             {settings.password_reset_token_expire_minutes} minutes. If you didn't request a reset,
             you can safely ignore this email — your password will not change.</p>
        </div>
        """
        text = (
            f"Hi {user_name},\n\n"
            f"Reset your PantryPulse password:\n{link}\n\n"
            f"This link expires in {settings.password_reset_token_expire_minutes} minutes. "
            f"If you didn't request this, ignore this email."
        )
        return self.send_email(user_email, subject, html, text)

    def send_password_changed_email(self, user_name: str, user_email: str) -> bool:
        subject = "Your PantryPulse password was changed"
        html = f"""
        <div style="font-family:Arial,Helvetica,sans-serif;max-width:560px;margin:auto;">
          <h2 style="color:#059669;">Password changed</h2>
          <p>Hi {user_name},</p>
          <p>Your PantryPulse password was recently changed. If this was you, no further
             action is needed.</p>
          <p style="color:#64748b;font-size:13px;">If you did <b>not</b> make this change,
             please contact your coordinator immediately and reset your password.</p>
        </div>
        """
        text = (
            f"Hi {user_name},\n\nYour PantryPulse password was recently changed. "
            f"If this was not you, contact your coordinator immediately."
        )
        return self.send_email(user_email, subject, html, text)
