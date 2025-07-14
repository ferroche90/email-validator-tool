"""Tests for domain_info module."""

from unittest.mock import Mock, patch

import pytest
from app.services.domain_info import _get_geo_data, get_domain_info


class TestDomainInfo:
    """Test domain information functionality."""

    @patch("app.services.domain_info.dns.resolver.resolve")
    @patch("app.services.domain_info.requests.get")
    def test_get_geo_data_success(self, mock_get, mock_resolve):
        """Test successful geo data retrieval."""
        # Mock DNS resolution
        mock_a_record = Mock()
        mock_a_record.to_text.return_value = "8.8.8.8"
        mock_resolve.return_value = [mock_a_record]

        # Mock IP-API.com response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"X-Rl": "44", "X-Ttl": "30"}
        mock_response.json.return_value = {
            "status": "success",
            "country": "United States",
            "regionName": "California",
            "city": "Mountain View",
            "zip": "94043",
        }
        mock_get.return_value = mock_response

        # Test the function
        result = _get_geo_data("google.com")

        # Verify the result
        assert result["country"] == "United States"
        assert result["region"] == "California"
        assert result["city"] == "Mountain View"
        assert result["zipcode"] == "94043"

        # Verify the API call
        mock_get.assert_called_once_with(
            "http://ip-api.com/json/8.8.8.8?fields=status,country,regionName,city,zip", timeout=10
        )

    @patch("app.services.domain_info.dns.resolver.resolve")
    @patch("app.services.domain_info.requests.get")
    def test_get_geo_data_rate_limited(self, mock_get, mock_resolve):
        """Test handling of rate limiting."""
        # Mock DNS resolution
        mock_a_record = Mock()
        mock_a_record.to_text.return_value = "8.8.8.8"
        mock_resolve.return_value = [mock_a_record]

        # Mock rate limit response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"X-Ttl": "60"}
        mock_get.return_value = mock_response

        # Test the function
        result = _get_geo_data("google.com")

        # Should return empty dict when rate limited
        assert result == {}

    @patch("app.services.domain_info.dns.resolver.resolve")
    def test_get_geo_data_dns_failure(self, mock_resolve):
        """Test handling of DNS resolution failure."""
        # Mock DNS resolution failure
        mock_resolve.side_effect = Exception("DNS resolution failed")

        # Test the function
        result = _get_geo_data("nonexistent-domain.com")

        # Should return empty dict when DNS fails
        assert result == {}

    @patch("app.services.domain_info.whois.whois")
    def test_get_domain_info_complete(self, mock_whois):
        """Test complete domain info retrieval."""
        # Mock WHOIS data
        mock_whois_data = Mock()
        mock_whois_data.creation_date = "2020-01-01 00:00:00"
        mock_whois.return_value = mock_whois_data

        # Mock other dependencies
        with (
            patch("app.services.domain_info._query_mx") as mock_mx,
            patch("app.services.domain_info._get_geo_data") as mock_geo,
            patch("app.services.domain_info._get_activity_data") as mock_activity,
            patch("app.services.domain_info._get_personal_data") as mock_personal,
        ):

            # Setup mocks
            mock_mx.return_value = ("mx.google.com", True)
            mock_geo.return_value = {
                "country": "United States",
                "region": "California",
                "city": "Mountain View",
                "zipcode": "94043",
            }
            mock_activity.return_value = "365+"
            mock_personal.return_value = {"firstname": "", "lastname": "", "gender": ""}

            # Test the function
            result = get_domain_info("google.com")

            # Verify core fields
            assert result["domain_age_days"] != ""
            assert result["mx_record"] == "mx.google.com"
            assert result["mx_found"] is True
            assert result["smtp_provider"] == "google"

            # Verify enhanced fields
            assert result["active_in_days"] == "365+"
            assert result["country"] == "United States"
            assert result["region"] == "California"
            assert result["city"] == "Mountain View"
            assert result["zipcode"] == "94043"

    def test_get_domain_info_no_whois(self):
        """Test domain info when WHOIS is not available."""
        with patch("app.services.domain_info.whois", None):
            with (
                patch("app.services.domain_info._query_mx") as mock_mx,
                patch("app.services.domain_info._get_geo_data") as mock_geo,
                patch("app.services.domain_info._get_activity_data") as mock_activity,
                patch("app.services.domain_info._get_personal_data") as mock_personal,
            ):

                # Setup mocks
                mock_mx.return_value = ("mx.example.com", True)
                mock_geo.return_value = {}
                mock_activity.return_value = ""
                mock_personal.return_value = {"firstname": "", "lastname": "", "gender": ""}

                # Test the function
                result = get_domain_info("example.com")

                # Should still work without WHOIS
                assert result["domain_age_days"] == ""
                assert result["mx_record"] == "mx.example.com"
                assert result["mx_found"] is True


if __name__ == "__main__":
    pytest.main([__file__])
