from pydantic_settings import BaseSettings
from functools import lru_cache

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

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
