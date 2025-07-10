import os
import secrets
from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration settings for the email validator"""

    # Environment configuration
    ENVIRONMENT: str = Field(default="dev", description="Environment: dev or prod")
    DEBUG: bool = Field(default=True, description="Debug mode")

    # JWT Configuration
    JWT_SECRET_KEY: str = Field(default="", description="JWT secret key (required in production)")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="JWT access token expiration in minutes")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="JWT refresh token expiration in days")
    
    # Security Configuration
    BCRYPT_WORK_FACTOR: int = Field(default=12, description="Bcrypt work factor for password hashing")
    MINIMUM_PASSWORD_LENGTH: int = Field(default=8, description="Minimum password length")
    
    # Database
    DATABASE_URL: str = Field(default="sqlite:///data/app.db", description="Database connection URL")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # CORS
    CORS_ORIGINS: str = Field(default="*", description="CORS allowed origins")

    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(default=60, description="Rate limit per minute")

    # SMTP settings
    SMTP_TIMEOUT: int = Field(default=10, description="SMTP timeout in seconds")
    SMTP_PORT: int = Field(default=25, description="SMTP port")
    MAX_CONCURRENT_CONNECTIONS: int = Field(default=10, description="Maximum concurrent connections")
    PER_DOMAIN_DELAY_SECONDS: float = Field(default=1.0, description="Delay between requests to the same domain")

    # DNS Cache settings
    ENABLE_DNS_CACHE: bool = Field(default=True, description="Enable DNS cache")
    DNS_CACHE_TTL_SECONDS: int = Field(default=3600, description="DNS cache TTL in seconds")
    CATCH_ALL_CACHE_TTL_SECONDS: int = Field(default=3600, description="Catch-all cache TTL in seconds")

    # Validation settings
    ENABLE_SMTP: bool = Field(default=False, description="Enable SMTP validation")
    ENABLE_CATCH_ALL: bool = Field(default=False, description="Enable catch-all detection")

    # CSV settings
    CSV_INPUT_PATH: str = Field(default="emails.csv", description="Input CSV file path")
    CSV_OUTPUT_PATH: str = Field(default="results.csv", description="Output CSV file path")

    # Observability settings
    METRICS_ALLOWLIST: str = Field(
        default="127.0.0.1,::1", description="Comma-separated list of IPs allowed to access metrics"
    )
    ENABLE_METRICS: bool = Field(default=True, description="Enable metrics collection and endpoints")

    # Data directory (can be overridden via env vars DATA_DIR or EMAIL_VALIDATOR_DATA_DIR)
    DATA_DIR: Optional[str] = Field(
        default=None, description="Absolute path to the shared data directory", env="DATA_DIR"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False

    @field_validator('JWT_SECRET_KEY', mode='before')
    @classmethod
    def validate_jwt_secret_key(cls, v):
        """Validate JWT secret key - generate secure default for dev, require env var for prod"""
        if not v or v == "":
            # Generate a secure random key for development
            return secrets.token_urlsafe(32)
        return v

    @field_validator('ENVIRONMENT')
    @classmethod
    def validate_environment(cls, v):
        """Validate environment setting"""
        if v not in ['dev', 'prod', 'test']:
            raise ValueError('ENVIRONMENT must be dev, prod, or test')
        return v

    def __init__(self, **kwargs):
        # Load environment-specific .env file before initializing
        self._load_environment_file()

        # Let BaseSettings process env vars / kwargs first
        super().__init__(**kwargs)

        # Validate production settings
        self._validate_production_settings()

        # Ensure DATA_DIR has a concrete value.  We resolve it via helper if
        # not provided explicitly (or via EMAIL_VALIDATOR_DATA_DIR env var).
        from email_validator_tool.utils.paths import get_data_dir

        if not self.DATA_DIR:
            # Fall back to helper – this will also create the directory
            self.DATA_DIR = str(get_data_dir())
        else:
            # If provided, make sure directory exists and normalise path
            from pathlib import Path

            data_path = Path(self.DATA_DIR).expanduser().resolve()
            data_path.mkdir(parents=True, exist_ok=True)
            self.DATA_DIR = str(data_path)

    def _load_environment_file(self):
        """Load environment-specific .env file based on ENVIRONMENT variable"""
        from dotenv import load_dotenv

        # Get environment from OS-level variable first, then default to dev
        environment = os.getenv("ENVIRONMENT", "dev")

        # Determine which .env file to load
        env_file = f".env.{environment}"

        # Load the environment-specific file if it exists
        if os.path.exists(env_file):
            load_dotenv(env_file)
        else:
            # Fallback to .env if environment-specific file doesn't exist
            if os.path.exists(".env"):
                load_dotenv(".env")

    def _validate_production_settings(self):
        """Validate that production settings are secure"""
        environment = os.getenv("ENVIRONMENT", "dev")
        debug = os.getenv("DEBUG", "true").lower() == "true"
        jwt_secret = os.getenv("JWT_SECRET_KEY")

        # Fail-fast assertions for production
        if environment == "prod":
            if debug:
                raise RuntimeError("❌ CRITICAL: DEBUG must be false in production environment")
            
            if not jwt_secret or jwt_secret == "dev-secret-key-change-in-production":
                raise RuntimeError("❌ CRITICAL: JWT_SECRET_KEY must be set to a secure value in production")
            
            if len(jwt_secret) < 32:
                raise RuntimeError("❌ CRITICAL: JWT_SECRET_KEY must be at least 32 characters long in production")
            
            # Check for HTTPS enforcement in CORS
            cors_origins = os.getenv("CORS_ORIGINS", "*")
            if cors_origins == "*":
                raise RuntimeError("❌ CRITICAL: CORS_ORIGINS must be explicitly set in production (not *)")
            
            if not any(origin.startswith("https://") for origin in cors_origins.split(",")):
                raise RuntimeError("❌ CRITICAL: CORS_ORIGINS must use HTTPS in production")

        # Additional security checks for any environment
        if jwt_secret and len(jwt_secret) < 16:
            raise RuntimeError("❌ CRITICAL: JWT_SECRET_KEY must be at least 16 characters long")


# Global settings instance
_settings_instance: Optional[Settings] = None


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance


def update_settings(enable_catch_all: Optional[bool] = None, enable_smtp: Optional[bool] = None) -> Settings:
    """
    Update settings dynamically and return the updated instance.
    This clears the cache to ensure fresh settings are used.

    Args:
        enable_catch_all: Optional value to set for ENABLE_CATCH_ALL
        enable_smtp: Optional value to set for ENABLE_SMTP

    Returns:
        Updated Settings instance
    """
    global _settings_instance

    # Clear the cache to force recreation
    get_settings.cache_clear()

    # Create new settings instance
    _settings_instance = Settings()

    # Apply updates if provided
    if enable_catch_all is not None:
        _settings_instance.ENABLE_CATCH_ALL = enable_catch_all
    if enable_smtp is not None:
        _settings_instance.ENABLE_SMTP = enable_smtp

    return _settings_instance
