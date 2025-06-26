"""Tests for catch-all caching and throttling functionality."""

import asyncio
import time
from unittest.mock import MagicMock, patch

import dns.resolver
import pytest
from email_validator_tool.core.models import ValidationStatus
from email_validator_tool.validators.catch_all import CatchAllValidator


@pytest.mark.asyncio
async def test_catch_all_cache_hit():
    """Test that second email from same domain hits cache and doesn't create new SMTP session."""
    validator = CatchAllValidator()

    # Mock DNS resolver to return valid MX records
    with patch("dns.resolver.resolve") as mock_resolve:
        mock_resolve.return_value = [MagicMock(exchange="mx.example.com")]

        # Mock SMTP to track calls
        with patch("aiosmtplib.SMTP") as mock_smtp:
            mock_smtp_instance = MagicMock()
            mock_smtp_instance.__aenter__.return_value = mock_smtp_instance
            mock_smtp_instance.__aexit__.return_value = None
            mock_smtp_instance.helo.return_value = None
            mock_smtp_instance.mail.return_value = None
            mock_smtp_instance.rcpt.return_value = (250, "OK")  # Catch-all response
            mock_smtp.return_value = mock_smtp_instance

            # First validation - should create SMTP session
            result1 = await validator.validate("test1@example.com")
            assert result1.status == ValidationStatus.CATCH_ALL
            assert mock_smtp_instance.rcpt.call_count == 1

            # Second validation - should use cache, no new SMTP session
            result2 = await validator.validate("test2@example.com")
            assert result2.status == ValidationStatus.CATCH_ALL
            # SMTP session count should still be 1 (no new session)
            assert mock_smtp_instance.rcpt.call_count == 1


@pytest.mark.asyncio
async def test_catch_all_cache_ttl():
    """Test that cache expires after TTL."""
    validator = CatchAllValidator()

    # Set a very short TTL for testing
    validator.settings.CATCH_ALL_CACHE_TTL_SECONDS = 0.1

    with patch("dns.resolver.resolve") as mock_resolve:
        mock_resolve.return_value = [MagicMock(exchange="mx.example.com")]

        with patch("aiosmtplib.SMTP") as mock_smtp:
            mock_smtp_instance = MagicMock()
            mock_smtp_instance.__aenter__.return_value = mock_smtp_instance
            mock_smtp_instance.__aexit__.return_value = None
            mock_smtp_instance.helo.return_value = None
            mock_smtp_instance.mail.return_value = None
            mock_smtp_instance.rcpt.return_value = (250, "OK")
            mock_smtp.return_value = mock_smtp_instance

            # First validation
            result1 = await validator.validate("test1@example.com")
            assert result1.status == ValidationStatus.CATCH_ALL
            assert mock_smtp_instance.rcpt.call_count == 1

            # Wait for cache to expire
            await asyncio.sleep(0.2)

            # Second validation - should create new SMTP session
            result2 = await validator.validate("test2@example.com")
            assert result2.status == ValidationStatus.CATCH_ALL
            assert mock_smtp_instance.rcpt.call_count == 2


@pytest.mark.asyncio
async def test_catch_all_throttling():
    """Test that throttling is enforced between requests to same domain."""
    validator = CatchAllValidator()
    validator.settings.PER_DOMAIN_DELAY_SECONDS = 0.1

    with patch("dns.resolver.resolve") as mock_resolve:
        mock_resolve.return_value = [MagicMock(exchange="mx.example.com")]

        with patch("aiosmtplib.SMTP") as mock_smtp:
            mock_smtp_instance = MagicMock()
            mock_smtp_instance.__aenter__.return_value = mock_smtp_instance
            mock_smtp_instance.__aexit__.return_value = None
            mock_smtp_instance.helo.return_value = None
            mock_smtp_instance.mail.return_value = None
            mock_smtp_instance.rcpt.return_value = (550, "User unknown")  # Not catch-all
            mock_smtp.return_value = mock_smtp_instance

            start_time = time.time()

            # First validation
            result1 = await validator.validate("test1@example.com")
            assert result1.status == ValidationStatus.VALID

            # Second validation immediately after - should be throttled
            result2 = await validator.validate("test2@example.com")
            assert result2.status == ValidationStatus.VALID

            end_time = time.time()

            # Should have taken at least the throttle delay
            assert end_time - start_time >= 0.1


@pytest.mark.asyncio
async def test_catch_all_cache_different_domains():
    """Test that cache is domain-specific."""
    validator = CatchAllValidator()

    with patch("dns.resolver.resolve") as mock_resolve:
        mock_resolve.return_value = [MagicMock(exchange="mx.example.com")]

        with patch("aiosmtplib.SMTP") as mock_smtp:
            mock_smtp_instance = MagicMock()
            mock_smtp_instance.__aenter__.return_value = mock_smtp_instance
            mock_smtp_instance.__aexit__.return_value = None
            mock_smtp_instance.helo.return_value = None
            mock_smtp_instance.mail.return_value = None
            mock_smtp_instance.rcpt.return_value = (250, "OK")
            mock_smtp.return_value = mock_smtp_instance

            # First domain
            result1 = await validator.validate("test@domain1.com")
            assert result1.status == ValidationStatus.CATCH_ALL
            assert mock_smtp_instance.rcpt.call_count == 1

            # Second domain - should create new SMTP session
            result2 = await validator.validate("test@domain2.com")
            assert result2.status == ValidationStatus.CATCH_ALL
            assert mock_smtp_instance.rcpt.call_count == 2


@pytest.mark.asyncio
async def test_catch_all_cache_invalid_domain():
    """Test that invalid domains are cached."""
    validator = CatchAllValidator()

    with patch("dns.resolver.resolve") as mock_resolve:
        mock_resolve.side_effect = dns.resolver.NXDOMAIN()

        # First validation
        result1 = await validator.validate("test@nonexistent.com")
        assert result1.status == ValidationStatus.INVALID_DOMAIN

        # Second validation - should use cache
        result2 = await validator.validate("test2@nonexistent.com")
        assert result2.status == ValidationStatus.INVALID_DOMAIN

        # DNS resolver should only be called once
        assert mock_resolve.call_count == 1
