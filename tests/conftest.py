"""
Common test fixtures for email validator tests.
"""

import pytest


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
