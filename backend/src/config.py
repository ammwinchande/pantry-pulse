"""
Centralized application settings (12-factor).

All configuration is exposed via environment variables / a `.env` file
located at the backend root (see `.env.example`).
"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/.env (resolved relative to this file so it works from any CWD)
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "PantryPulse API"
    environment: str = "development"  # development | staging | production
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    static_dir: str = ""

    # --- Logging ---
    # Console/file verbosity: DEBUG | INFO | WARNING | ERROR (default INFO).
    log_level: str = "INFO"
    # Optional path to a rotating log file. Empty = console only.
    # Set in production (e.g. /app/logs/pantrypulse.log) for retention.
    log_file: str = ""

    # --- Persistence (datastore) ---
    # SQLAlchemy URL. SQLite by default (zero-config); switch to Postgres/MySQL
    # in production by setting this, e.g.:
    #   postgresql+psycopg://user:pass@host:5432/pantrypulse
    #   mysql+pymysql://user:pass@host:3306/pantrypulse
    database_url: str = "sqlite:///pantrypulse.db"
    # When true, load demo/seed data on boot (idempotent). Disable in prod.
    seed_on_startup: bool = True

    # --- JWT / Auth ---
    jwt_secret_key: str = "dev-only-secret-change-me-0123456789abcdef"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    email_verification_token_expire_minutes: int = 120
    password_reset_token_expire_minutes: int = 30
    # Demo aid: when true (development only), register/reset responses include
    # the activation/reset URL so judges can complete the flow without an inbox.
    expose_dev_tokens: bool = True

    # --- Mailtrap (password reset / change / registration activation emails) ---
    mailtrap_api_key: str = ""
    mailtrap_sender_email: str = "pantrypulse@sandbox.mailtrap.io"
    mailtrap_sender_name: str = "PantryPulse"
    app_base_url: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
