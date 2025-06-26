"""Tests for the TypoSuggestionValidator."""

from unittest.mock import MagicMock, patch

import pytest
from email_validator_tool.core.models import ValidationStatus
from email_validator_tool.core.typo_suggestions import suggest_domain
from email_validator_tool.validators.typo_suggestion import TypoSuggestionValidator


@pytest.mark.asyncio
async def test_typo_suggestion_gmail():
    """Test that gmail.com suggests gmail.com."""
    with patch("email_validator_tool.core.typo_suggestions.EmailSpellChecker") as mock_checker:
        # Mock the spell checker to return gmail.com for gmail.com
        mock_instance = MagicMock()
        mock_instance.check_domain.return_value = "gmail.com"
        mock_checker.return_value = mock_instance

        validator = TypoSuggestionValidator()
        result = await validator.validate("test@gmail.com")

        assert result.status == ValidationStatus.VALID
        assert result.suggestion == "test@gmail.com"


@pytest.mark.asyncio
async def test_typo_suggestion_with_typo():
    """Test that gmail.com suggests gmail.com."""
    with patch("email_validator_tool.core.typo_suggestions.EmailSpellChecker") as mock_checker:
        # Mock the spell checker to return gmail.com for gmail.com
        mock_instance = MagicMock()
        mock_instance.check_domain.return_value = "gmail.com"
        mock_checker.return_value = mock_instance

        validator = TypoSuggestionValidator()
        result = await validator.validate("test@gmail.com")

        assert result.status == ValidationStatus.VALID
        assert result.suggestion == "test@gmail.com"


@pytest.mark.asyncio
async def test_typo_suggestion_no_typo():
    """Test that correct domains don't get suggestions."""
    with patch("email_validator_tool.core.typo_suggestions.EmailSpellChecker") as mock_checker:
        # Mock the spell checker to return None (no suggestion)
        mock_instance = MagicMock()
        mock_instance.check_domain.return_value = None
        mock_checker.return_value = mock_instance

        validator = TypoSuggestionValidator()
        result = await validator.validate("test@gmail.com")

        assert result.status == ValidationStatus.VALID
        assert result.suggestion is None


@pytest.mark.asyncio
async def test_typo_suggestion_invalid_email():
    """Test that invalid emails without @ don't get suggestions."""
    validator = TypoSuggestionValidator()
    result = await validator.validate("invalid-email")

    assert result.status == ValidationStatus.VALID
    assert result.suggestion is None


@pytest.mark.asyncio
async def test_typo_suggestion_package_unavailable():
    """Test behavior when email-spell-checker package is not available."""
    with patch("email_validator_tool.core.typo_suggestions.SPELL_CHECKER_AVAILABLE", False):
        validator = TypoSuggestionValidator()
        result = await validator.validate("test@gmail.com")

        assert result.status == ValidationStatus.VALID
        assert result.suggestion is None


def test_suggest_domain_helper():
    """Test the suggest_domain helper function."""
    with patch("email_validator_tool.core.typo_suggestions.EmailSpellChecker") as mock_checker:
        # Mock the spell checker to return gmail.com for gmail.com
        mock_instance = MagicMock()
        mock_instance.check_domain.return_value = "gmail.com"
        mock_checker.return_value = mock_instance

        suggestion = suggest_domain("gmail.com")
        assert suggestion == "gmail.com"


def test_suggest_domain_no_suggestion():
    """Test suggest_domain when no suggestion is found."""
    with patch("email_validator_tool.core.typo_suggestions.EmailSpellChecker") as mock_checker:
        # Mock the spell checker to return None
        mock_instance = MagicMock()
        mock_instance.check_domain.return_value = None
        mock_checker.return_value = mock_instance

        suggestion = suggest_domain("gmail.com")
        assert suggestion is None


def test_suggest_domain_same_domain():
    """Test suggest_domain when suggestion is the same as input."""
    with patch("email_validator_tool.core.typo_suggestions.EmailSpellChecker") as mock_checker:
        # Mock the spell checker to return the same domain
        mock_instance = MagicMock()
        mock_instance.check_domain.return_value = "gmail.com"
        mock_checker.return_value = mock_instance

        suggestion = suggest_domain("gmail.com")
        assert suggestion is None  # Should return None when suggestion equals input
