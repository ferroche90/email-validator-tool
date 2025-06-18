from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuration settings for the email validator."""
    
    # Enable/disable validation phases
    ENABLE_CATCH_ALL: bool = False
    ENABLE_SMTP: bool = False
    
    # SMTP settings
    SMTP_TIMEOUT: int = 10
    SMTP_PORT: int = 25
    
    # General parameters
    CSV_INPUT_PATH: str = "emails.csv"
    CSV_OUTPUT_PATH: str = "results.csv"

    # Concurrency and timeouts
    MAX_CONCURRENT_CONNECTIONS: int = 10
    PER_DOMAIN_DELAY_SECONDS: float = 5.0

    class Config:
        env_prefix = "EMAIL_VALIDATOR_"
