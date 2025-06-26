"""
Common test fixtures for email validator tests.
"""

import os
import time
from unittest.mock import patch

import pytest
from app.main import app
from email_validator_tool.core.pipeline import ValidationPipeline
from email_validator_tool.core.results import ValidationResult
from fastapi.testclient import TestClient

# Set test environment variables to increase rate limits for testing
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"
os.environ["RATE_LIMIT_PER_MINUTE"] = "1000"  # High rate limit for tests


@pytest.fixture
def valid_email():
    """Return a valid email address for testing."""
    return "john.doe@example.com"


@pytest.fixture
def invalid_email():
    """Return an invalid email address for testing."""
    return "invalid@email"


@pytest.fixture
def disposable_email():
    """Return a disposable email address for testing."""
    return "test@mailinator.com"


@pytest.fixture
def role_account_email():
    """Return a role account email address for testing."""
    return "admin@example.com"


@pytest.fixture
def validation_result():
    """Return a ValidationResult instance for testing."""
    return ValidationResult()


@pytest.fixture
def validation_pipeline():
    """Return a ValidationPipeline instance for testing."""
    return ValidationPipeline(enable_smtp=False, enable_catch_all=False)


@pytest.fixture
def client():
    """FastAPI TestClient with overridden settings for testing."""
    with patch("email_validator_tool.config.get_settings") as mock_settings:
        # Override settings for testing
        mock_settings.return_value.ENABLE_DNS_CACHE = False
        mock_settings.return_value.DNS_CACHE_TTL_SECONDS = 0
        mock_settings.return_value.ENABLE_SMTP = False
        mock_settings.return_value.ENABLE_CATCH_ALL = False
        mock_settings.return_value.MAX_CONCURRENT_CONNECTIONS = 1
        mock_settings.return_value.SMTP_TIMEOUT = 1

        with TestClient(app) as test_client:
            # Create the expected API keys in the key manager for testing
            from email_validator_tool.key_manager import create_key_manager

            key_manager = create_key_manager()

            # Create test API keys if they don't exist
            # We'll create them with the expected values from settings
            if not key_manager.validate_key("test_user_api_key"):
                # Create a user key with the expected value
                user_key = key_manager.create_key("user")
                # Replace the generated key with our test key
                key_manager.keys["test_user_api_key"] = key_manager.keys.pop(user_key.key)
                key_manager.keys["test_user_api_key"].key = "test_user_api_key"
                key_manager._save_keys()

            if not key_manager.validate_key("test_admin_api_key"):
                # Create an admin key with the expected value
                admin_key = key_manager.create_key("admin")
                # Replace the generated key with our test key
                key_manager.keys["test_admin_api_key"] = key_manager.keys.pop(admin_key.key)
                key_manager.keys["test_admin_api_key"].key = "test_admin_api_key"
                key_manager._save_keys()

            yield test_client


def get_token_safely(client: TestClient, api_key: str, max_retries: int = 3):
    """Safely retrieve a JWT token from the API, retrying if rate limited."""
    for attempt in range(max_retries):
        response = client.post("/api/token", json={"api_key": api_key})

        if response.status_code == 200:
            return response.json()["access_token"]
        elif response.status_code == 429:  # Rate limited
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait 1 second before retrying
                continue
            pytest.skip("Rate limited after retries")
        else:
            pytest.fail(f"Token request failed with status {response.status_code}: {response.text}")

    pytest.fail("Failed to obtain token after all retries")
