"""
SportSkyline Backend — Application Configuration
Reads from .env file via pydantic-settings.
"""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "SportSkyline"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    secret_key: str = "CHANGE_ME"

    # JWT
    jwt_secret_key: str = "CHANGE_ME"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 30

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/sportskyline"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_storage_bucket: str = "sportskyline-media"

    # Admin bootstrap
    first_admin_email: str = "admin@sportskyline.com"
    first_admin_password: str = "Admin@123!"
    first_admin_name: str = "Super Admin"

    # Rate limiting
    rate_limit_public: str = "60/minute"
    rate_limit_admin: str = "200/minute"

    # Pagination
    default_page_size: int = 10
    max_page_size: int = 100

    # CORS — stored as comma-separated string, parsed to list
    cors_origins: str = "http://localhost:5500,http://127.0.0.1:5500"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    # Media
    max_upload_size_mb: int = 10
    allowed_image_types: str = "image/jpeg,image/png,image/webp,image/gif"

    @property
    def allowed_image_types_list(self) -> List[str]:
        return [t.strip() for t in self.allowed_image_types.split(",") if t.strip()]

    # Background Jobs
    trending_recompute_interval_minutes: int = 15
    scheduled_publish_check_interval_minutes: int = 1

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
