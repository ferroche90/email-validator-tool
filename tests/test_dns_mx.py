from unittest.mock import MagicMock, patch

import pytest
from dns.resolver import NXDOMAIN, NoAnswer

from email_validator_tool.models import ValidationStatus
from email_validator_tool.validators.dns_mx import check


@pytest.mark.asyncio
async def test_valid_mx_records():
    """Test that a domain with valid MX records passes validation."""
    # Mock MX records response
    mock_mx = MagicMock()
    mock_mx.exchange = "mail.example.com"
    mock_response = [mock_mx]

    with patch("dns.resolver.resolve", return_value=mock_response):
        result = await check("user@example.com")
        assert result.status == ValidationStatus.VALID
        assert result.details is None


@pytest.mark.asyncio
async def test_nonexistent_domain():
    """Test that a non-existent domain fails validation."""
    with patch("dns.resolver.resolve", side_effect=NXDOMAIN):
        result = await check("user@nonexistent.com")
        assert result.status == ValidationStatus.INVALID_DOMAIN
        assert "domain does not exist" in result.details.lower()


@pytest.mark.asyncio
async def test_no_mx_records():
    """Test that a domain without MX records fails validation."""
    with patch("dns.resolver.resolve", side_effect=NoAnswer):
        result = await check("user@nomx.com")
        assert result.status == ValidationStatus.INVALID_MX
        assert "no mx records" in result.details.lower()


@pytest.mark.asyncio
async def test_empty_mx_records():
    """Test that a domain with empty MX records fails validation."""
    with patch("dns.resolver.resolve", return_value=[]):
        result = await check("user@example.com")
        assert result.status == ValidationStatus.INVALID_MX
        assert "no mx records" in result.details.lower()


@pytest.mark.asyncio
async def test_dns_resolver_error():
    """Test that a DNS resolver error returns unknown error status."""
    with patch("dns.resolver.resolve", side_effect=Exception("DNS error")):
        result = await check("user@example.com")
        assert result.status == ValidationStatus.UNKNOWN_ERROR
        assert "dns error" in result.details.lower()
