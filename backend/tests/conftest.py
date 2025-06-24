"""
Common test fixtures for email validator tests.
"""

import os
from unittest.mock import patch

import pytest
from app.main import app
from fastapi.testclient import TestClient

from email_validator_tool.core.pipeline import ValidationPipeline
from email_validator_tool.core.results import ValidationResult


@pytest.fixture
def valid_email():
    """Return a valid email address for testing."""
    return "test@example.com"


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
    # Set test API token to admin_token_here for admin tests
    os.environ["API_TOKEN"] = "admin_token_here"
    
    with patch("email_validator_tool.config.get_settings") as mock_settings:
        # Override settings for testing
        mock_settings.return_value.ENABLE_DNS_CACHE = False
        mock_settings.return_value.DNS_CACHE_TTL_SECONDS = 0
        mock_settings.return_value.ENABLE_SMTP = False
        mock_settings.return_value.ENABLE_CATCH_ALL = False
        mock_settings.return_value.MAX_CONCURRENT_CONNECTIONS = 1
        mock_settings.return_value.SMTP_TIMEOUT = 1

        with TestClient(app) as test_client:
            # Removed rate limiter reset (reset_all does not exist)
            yield test_client
