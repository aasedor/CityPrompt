"""
Application configuration using pydantic-settings.
Loads from environment variables and .env file.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import List

from dotenv import dotenv_values
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent

# Pre-load GOOGLE_APPLICATION_CREDENTIALS from .env into os.environ so that
# google.auth.default() can discover it before Settings is constructed.
_dotenv = dotenv_values(_BACKEND_ROOT / ".env")
_root_dotenv = dotenv_values(_BACKEND_ROOT.parent / ".env")
if _gac := _dotenv.get("GOOGLE_APPLICATION_CREDENTIALS"):
    # Resolve relative paths against the backend root directory
    _gac_path = Path(_gac)
    if not _gac_path.is_absolute():
        _gac_path = (_BACKEND_ROOT / _gac_path).resolve()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(_gac_path)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_env: str = "development"
    app_debug: bool = False
    app_name: str = "3D Development Platform"
    app_version: str = "0.1.0"

    # --- Database ---
    database_url: str = "postgresql+asyncpg://devuser:devpassword@localhost:5432/dev_platform"
    database_url_sync: str = "postgresql://devuser:devpassword@localhost:5432/dev_platform"

    @model_validator(mode="after")
    def _normalize_database_urls(self) -> "Settings":
        """Handle Render's postgres:// URL format.

        Render provides DATABASE_URL as postgres://... which needs:
        - postgresql+asyncpg:// for the async engine
        - postgresql:// for sync (Alembic / Celery)
        """
        url = self.database_url
        # Render gives postgres:// — SQLAlchemy needs postgresql://
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        # Ensure async driver is present
        if url.startswith("postgresql://"):
            async_url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            self.database_url = async_url
        # Derive sync URL by stripping +asyncpg
        self.database_url_sync = self.database_url.replace("+asyncpg", "")
        return self

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- Security ---
    jwt_secret_key: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    allowed_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:5174,http://127.0.0.1:5174,"
        "http://localhost:5175,http://127.0.0.1:5175,"
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:3001,http://127.0.0.1:3001"
    )

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    # --- SMTP (Password Reset Emails) ---
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_sender: str = ""

    # --- OAuth2 Social Login ---
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/oauth/google/callback"
    microsoft_client_id: str = ""
    microsoft_client_secret: str = ""
    microsoft_redirect_uri: str = "http://localhost:8000/api/v1/auth/oauth/microsoft/callback"
    frontend_url: str = "http://localhost:5175"

    # --- API Keys ---
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    mapbox_access_token: str = ""
    meshy_api_key: str = ""
    meshy_api_base: str = "https://api.meshy.ai"
    stability_api_key: str = ""
    stability_api_base: str = "https://api.stability.ai"
    tripo_api_key: str = ""
    tripo_api_base: str = "https://api.tripo3d.ai"
    default_generation_engine: str = "meshy"
    gemini_api_key: str = ""
    google_maps_api_key: str = ""
    fal_key: str = ""
    fal_style_model: str = "fal-ai/fast-sdxl/image-to-image"
    gemini_2d_image_model: str = "gemini-3-pro-image-preview"
    master_plan_2d_style_model: str = "gemini-3.1-flash-image-preview"
    master_plan_2d_image_provider: str = "vertex"
    master_plan_3d_image_provider: str = "vertex"
    layout_ai_provider: str = "claude"

    @model_validator(mode="after")
    def _normalize_openai_api_key(self) -> "Settings":
        """Accept the temporary OPENAI alias while local testing GPT Image 2."""
        if not self.openai_api_key:
            self.openai_api_key = (
                os.environ.get("OPENAI", "")
                or _dotenv.get("OPENAI", "")
                or _root_dotenv.get("OPENAI", "")
            )
        return self

    # --- Vertex AI (Imagen 3) ---
    vertex_ai_project: str = ""
    vertex_ai_location: str = "northamerica-northeast1"
    vertex_ai_imagen_model: str = "imagen-3.0-capability-001"
    google_application_credentials: str = ""

    @model_validator(mode="after")
    def _set_gcloud_credentials_env(self) -> "Settings":
        """Propagate GOOGLE_APPLICATION_CREDENTIALS to os.environ so that
        google.auth.default() can discover the service-account key."""
        if self.google_application_credentials and not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            cred_path = Path(self.google_application_credentials)
            if not cred_path.is_absolute():
                cred_path = (_BACKEND_ROOT / cred_path).resolve()
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(cred_path)
        return self

    # --- Object Storage ---
    s3_bucket_name: str = "dev-platform-uploads"
    s3_region: str = "us-east-1"
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"

    # --- Monitoring ---
    sentry_dsn: str = ""
    log_level: str = "INFO"

    # --- Upload Limits ---
    max_upload_size_mb: int = 100
    processing_workers: int = 2

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache()
def get_settings() -> Settings:
    return Settings()
