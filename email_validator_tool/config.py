import os
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration settings for the email validator"""

    # Environment configuration
    ENVIRONMENT: str = Field(default="dev", description="Environment: dev or prod")
    DEBUG: bool = Field(default=True, description="Debug mode")

    # API Configuration
    API_TOKEN: str = Field(default="dev_token_here", description="API authentication token")
    ADMIN_TOKEN: str = Field(default="dev_admin_token_here", description="Admin authentication token")

    # Database
    DATABASE_URL: str = Field(default="sqlite:///app.db", description="Database connection URL")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # CORS
    CORS_ORIGINS: str = Field(default="*", description="CORS allowed origins")

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Rate limit per minute")

    # SMTP settings
    SMTP_TIMEOUT: int = Field(default=10, description="SMTP timeout in seconds")
    SMTP_PORT: int = Field(default=25, description="SMTP port")
    MAX_CONCURRENT_CONNECTIONS: int = Field(default=10, description="Maximum concurrent connections")
    PER_DOMAIN_DELAY_SECONDS: float = Field(default=5.0, description="Delay between domain requests")

    # Optional features
    ENABLE_CATCH_ALL: bool = Field(default=False, description="Enable catch-all detection")
    ENABLE_SMTP: bool = Field(default=False, description="Enable SMTP verification")

    # General parameters
    CSV_INPUT_PATH: str = Field(default="emails.csv", description="Default CSV input path")
    CSV_OUTPUT_PATH: str = Field(default="results.csv", description="Default CSV output path")

    # DNS Cache settings
    ENABLE_DNS_CACHE: bool = Field(default=True, description="Enable DNS caching")
    DNS_CACHE_TTL_SECONDS: int = Field(default=3600, description="DNS cache TTL in seconds")

    class Config:
        env_file = None  # We'll handle this manually
        case_sensitive = True

    def __init__(self, **kwargs):
        # Load environment-specific .env file before initializing
        self._load_environment_file()
        
        # Validate production settings
        self._validate_production_settings()
        
        super().__init__(**kwargs)

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
        
        if environment == "prod" and debug:
            raise RuntimeError("DEBUG must be false in production environment")


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
