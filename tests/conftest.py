"""
Common test fixtures for email validator tests.
"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

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

