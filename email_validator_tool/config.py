from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration settings for the email validator"""

    # SMTP settings
    SMTP_TIMEOUT: int = 10
    SMTP_PORT: int = 25
    MAX_CONCURRENT_CONNECTIONS: int = 10

    # Optional features
    ENABLE_CATCH_ALL: bool = False
    ENABLE_SMTP: bool = False

    # Validation thresholds
    MIN_MX_RECORDS: int = 1
    MAX_BOUNCE_RATE: float = 0.1

    # General parameters
    CSV_INPUT_PATH: str = "emails.csv"
    CSV_OUTPUT_PATH: str = "results.csv"

    # Concurrency and timeouts
    PER_DOMAIN_DELAY_SECONDS: float = 5.0

    # DNS Cache settings
    ENABLE_DNS_CACHE: bool = True
    DNS_CACHE_TTL_SECONDS: int = 3600  # 1 hour default

    class Config:
        env_file = ".env"
        case_sensitive = True


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
