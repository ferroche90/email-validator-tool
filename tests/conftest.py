"""
Common test fixtures for email validator tests.
"""

import pytest
from email_validator_tool.core.results import ValidationResult
from email_validator_tool.core.pipeline import ValidationPipeline

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
    return ValidationPipeline()
