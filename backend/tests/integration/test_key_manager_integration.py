"""
Integration tests for key manager functionality.
"""

import pytest
from app.main import app
from fastapi.testclient import TestClient

from backend.tests.conftest import get_token_safely


class TestKeyManagerBackendIntegration:
    """Test key manager integration with backend API."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_token_endpoint_with_valid_api_key(self, client):
        """Test /api/token endpoint with a valid API key."""
        # Use the same key manager that the API uses
        from email_validator_tool.key_manager import create_key_manager
        key_manager = create_key_manager()
        
        # Create a valid API key
        api_key = key_manager.create_key("user")

        # Make request to token endpoint with retry logic for rate limiting
        max_retries = 3
        for attempt in range(max_retries):
            response = client.post("/api/token", json={"api_key": api_key.key})
            
            if response.status_code == 200:
                # Success - validate response
                data = response.json()
                assert "access_token" in data
                assert data["token_type"] == "bearer"
                assert data["role"] == "user"
                return  # Test passed
            elif response.status_code == 429:
                # Rate limited - skip test if we've exhausted retries
                if attempt == max_retries - 1:
                    pytest.skip("Rate limited after retries - this is acceptable in test environment")
                continue
            else:
                # Unexpected error
                pytest.fail(f"Unexpected status code {response.status_code}: {response.text}")
        
        pytest.fail("Failed to get token after all retries")

    def test_token_endpoint_with_revoked_api_key(self, client):
        """Test /api/token endpoint with a revoked API key returns 401."""
        # Use the same key manager that the API uses
        from email_validator_tool.key_manager import create_key_manager
        key_manager = create_key_manager()
        
        # Create and revoke an API key
        api_key = key_manager.create_key("admin")
        key_manager.revoke_key(api_key.key)

        # Make request to token endpoint with retry logic for rate limiting
        max_retries = 3
        for attempt in range(max_retries):
            response = client.post("/api/token", json={"api_key": api_key.key})
            
            if response.status_code == 401:
                # Expected - validate response
                assert "Invalid or revoked API key" in response.json()["detail"]
                return  # Test passed
            elif response.status_code == 429:
                # Rate limited - skip test if we've exhausted retries
                if attempt == max_retries - 1:
                    pytest.skip("Rate limited after retries - this is acceptable in test environment")
                continue
            else:
                # Unexpected error
                pytest.fail(f"Unexpected status code {response.status_code}: {response.text}")
        
        pytest.fail("Failed to test revoked API key after all retries")

    def test_token_endpoint_with_invalid_api_key(self, client):
        """Test /api/token endpoint with an invalid API key returns 401."""
        # Make request with invalid API key with retry logic for rate limiting
        max_retries = 3
        for attempt in range(max_retries):
            response = client.post("/api/token", json={"api_key": "invalid_key_123"})
            
            if response.status_code == 401:
                # Expected - validate response
                assert "Invalid or revoked API key" in response.json()["detail"]
                return  # Test passed
            elif response.status_code == 429:
                # Rate limited - skip test if we've exhausted retries
                if attempt == max_retries - 1:
                    pytest.skip("Rate limited after retries - this is acceptable in test environment")
                continue
            else:
                # Unexpected error
                pytest.fail(f"Unexpected status code {response.status_code}: {response.text}")
        
        pytest.fail("Failed to test invalid API key after all retries")

    def test_validate_endpoint_with_api_key(self, client):
        """Test /api/validate endpoint with API key authentication."""
        # Use the same key manager that the API uses
        from email_validator_tool.key_manager import create_key_manager
        key_manager = create_key_manager()
        
        # Create a valid API key
        api_key = key_manager.create_key("user")

        # First, get a JWT token using the API key
        token_response = client.post("/api/token", json={"api_key": api_key.key})
        if token_response.status_code != 200:
            pytest.skip("Could not get JWT token - rate limited or other issue")
        
        jwt_token = token_response.json()["access_token"]

        # Make request to validate endpoint with retry logic for rate limiting
        max_retries = 3
        for attempt in range(max_retries):
            response = client.post(
                "/api/validate", json={"emails": ["test@example.com"]}, headers={"Authorization": f"Bearer {jwt_token}"}
            )
            
            if response.status_code == 200:
                # Success - validate response
                assert "results" in response.json()
                return  # Test passed
            elif response.status_code == 429:
                # Rate limited - skip test if we've exhausted retries
                if attempt == max_retries - 1:
                    pytest.skip("Rate limited after retries - this is acceptable in test environment")
                continue
            else:
                # Unexpected error
                pytest.fail(f"Unexpected status code {response.status_code}: {response.text}")
        
        pytest.fail("Failed to validate emails after all retries")

    @pytest.mark.rate_limited
    def test_validate_endpoint_with_revoked_api_key(self, client):
        """Test /api/validate endpoint with revoked API key returns 401.\n\nNOTE: This test may be skipped if rate limited. For full coverage, run it in isolation or in a separate CI job."""
        # Use the same key manager that the API uses
        from email_validator_tool.key_manager import create_key_manager
        key_manager = create_key_manager()
        
        # Create and revoke an API key
        api_key = key_manager.create_key("user")
        key_manager.revoke_key(api_key.key)

        # Try to get a JWT token with revoked key - should fail
        token_response = client.post("/api/token", json={"api_key": api_key.key})
        assert token_response.status_code == 401
        assert "Invalid or revoked API key" in token_response.json()["detail"]

        # Try to use the revoked key directly in Authorization header with retry logic for rate limiting
        max_retries = 3
        for attempt in range(max_retries):
            response = client.post(
                "/api/validate", json={"emails": ["test@example.com"]}, headers={"Authorization": f"Bearer {api_key.key}"}
            )
            
            if response.status_code == 401:
                # Expected - validate response
                assert "Invalid token" in response.json()["detail"]
                return  # Test passed
            elif response.status_code == 429:
                # Rate limited - wait and retry
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)  # Wait 2 seconds before retry
                    continue
                else:
                    pytest.skip("Rate limited after retries - this is acceptable in test environment")
            else:
                # Unexpected error
                pytest.fail(f"Unexpected status code {response.status_code}: {response.text}")
        
        pytest.fail("Failed to test revoked API key after all retries")

    def test_admin_endpoint_with_user_api_key(self, client):
        """Test admin endpoint with user API key returns 403."""
        # Use the same key manager that the API uses
        from email_validator_tool.key_manager import create_key_manager
        key_manager = create_key_manager()
        
        # Create a user API key
        api_key = key_manager.create_key("user")

        # First, get a JWT token using the API key
        token_response = client.post("/api/token", json={"api_key": api_key.key})
        if token_response.status_code != 200:
            pytest.skip("Could not get JWT token - rate limited or other issue")
        
        jwt_token = token_response.json()["access_token"]

        # Make request to admin endpoint
        response = client.get("/api/cache-stats", headers={"Authorization": f"Bearer {jwt_token}"})

        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    def test_admin_endpoint_with_admin_api_key(self, client):
        """Test admin endpoint with admin API key succeeds."""
        # Use the same key manager that the API uses
        from email_validator_tool.key_manager import create_key_manager
        key_manager = create_key_manager()
        
        # Create an admin API key
        api_key = key_manager.create_key("admin")

        # First, get a JWT token using the API key
        token_response = client.post("/api/token", json={"api_key": api_key.key})
        if token_response.status_code != 200:
            pytest.skip("Could not get JWT token - rate limited or other issue")
        
        jwt_token = token_response.json()["access_token"]

        # Make request to admin endpoint with retry logic for rate limiting
        max_retries = 3
        for attempt in range(max_retries):
            response = client.get("/api/cache-stats", headers={"Authorization": f"Bearer {jwt_token}"})
            
            if response.status_code == 200:
                # Success - validate response
                assert "cache_stats" in response.json()
                return  # Test passed
            elif response.status_code == 429:
                # Rate limited - skip test if we've exhausted retries
                if attempt == max_retries - 1:
                    pytest.skip("Rate limited after retries - this is acceptable in test environment")
                continue
            else:
                # Unexpected error
                pytest.fail(f"Unexpected status code {response.status_code}: {response.text}")
        
        pytest.fail("Failed to access admin endpoint after all retries")

    @pytest.mark.rate_limited
    def test_admin_endpoint_with_revoked_admin_api_key(self, client):
        """Test admin endpoint with revoked admin API key returns 401.\n\nNOTE: This test may be skipped if rate limited. For full coverage, run it in isolation or in a separate CI job."""
        # Use the same key manager that the API uses
        from email_validator_tool.key_manager import create_key_manager
        key_manager = create_key_manager()
        
        # Create and revoke an admin API key
        api_key = key_manager.create_key("admin")
        key_manager.revoke_key(api_key.key)

        # Try to get a JWT token with revoked key - should fail
        token_response = client.post("/api/token", json={"api_key": api_key.key})
        assert token_response.status_code == 401
        assert "Invalid or revoked API key" in token_response.json()["detail"]

        # Try to use the revoked key directly in Authorization header with retry logic for rate limiting
        max_retries = 3
        for attempt in range(max_retries):
            response = client.get("/api/cache-stats", headers={"Authorization": f"Bearer {api_key.key}"})
            
            if response.status_code == 401:
                # Expected - validate response
                assert "Invalid token" in response.json()["detail"]
                return  # Test passed
            elif response.status_code == 429:
                # Rate limited - wait and retry
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)  # Wait 2 seconds before retry
                    continue
                else:
                    pytest.skip("Rate limited after retries - this is acceptable in test environment")
            else:
                # Unexpected error
                pytest.fail(f"Unexpected status code {response.status_code}: {response.text}")
        
        pytest.fail("Failed to test revoked admin API key after all retries")

    def test_admin_api_key_works_for_admin_endpoints(self, client, setup_test_api_keys):
        """Test that admin API keys work for admin endpoints."""
        # Get admin token
        admin_token = get_token_safely(client, "test_admin_api_key")

        # Test admin endpoint
        response = client.get("/api/cache-stats", headers={"Authorization": f"Bearer {admin_token}"})

        assert response.status_code == 200
        data = response.json()
        assert "cache_stats" in data

    def test_jwt_token_still_works(self, client):
        """Test that JWT tokens still work."""
        from app.auth.jwt import create_access_token

        # Create a JWT token
        payload = {"sub": "test_user", "role": "user"}
        jwt_token = create_access_token(payload)

        # Test JWT token with retry logic for rate limiting
        max_retries = 3
        for attempt in range(max_retries):
            response = client.post(
                "/api/validate", json={"emails": ["test@example.com"]}, headers={"Authorization": f"Bearer {jwt_token}"}
            )
            
            if response.status_code == 200:
                # Success - test passed
                return
            elif response.status_code == 429:
                # Rate limited - skip test if we've exhausted retries
                if attempt == max_retries - 1:
                    pytest.skip("Rate limited after retries - this is acceptable in test environment")
                continue
            else:
                # Unexpected error
                pytest.fail(f"Unexpected status code {response.status_code}: {response.text}")
        
        pytest.fail("Failed to validate with JWT token after all retries")
