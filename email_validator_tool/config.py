from pydantic import BaseSettings

class Settings(BaseSettings):
    # General parameters
    CSV_INPUT_PATH: str = "emails.csv"
    CSV_OUTPUT_PATH: str = "results.csv"

    # Concurrency and timeouts
    MAX_CONCURRENT_CONNECTIONS: int = 10
    PER_DOMAIN_DELAY_SECONDS: float = 5.0
    SMTP_TIMEOUT: int = 10

    # Flags to enable risky layers
    ENABLE_CATCH_ALL: bool = False
    ENABLE_SMTP: bool = False

    class Config:
        env_file = ".env"
