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

    def test_token_endpoint_with_valid_api_key(self, client, reset_limits, no_rate_limit):
        """Test /api/token endpoint with a valid API key."""
        # Use the same key manager that the API uses
        from email_validator_tool.key_manager import create_key_manager
        key_manager = create_key_manager()
        
        # Create a valid API key
        api_key = key_manager.create_key("user")

        # Make request to token endpoint
        response = client.post("/api/token", json={"api_key": api_key.key})
        
        # Should succeed
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "user"

    def test_token_endpoint_with_revoked_api_key(self, client, reset_limits, no_rate_limit):
        """Test /api/token endpoint with a revoked API key returns 401."""
        # Use the same key manager that the API uses
        from email_validator_tool.key_manager import create_key_manager
        key_manager = create_key_manager()
        
        # Create and revoke an API key
        api_key = key_manager.create_key("admin")
        key_manager.revoke_key(api_key.key)

        # Make request to token endpoint
        response = client.post("/api/token", json={"api_key": api_key.key})
        
        # Should fail with 401
        assert response.status_code == 401
        assert "Invalid or revoked API key" in response.json()["detail"]

    def test_token_endpoint_with_invalid_api_key(self, client, reset_limits, no_rate_limit):
        """Test /api/token endpoint with an invalid API key returns 401."""
        # Make request with invalid API key
        response = client.post("/api/token", json={"api_key": "invalid_key_123"})
        
        # Should fail with 401
        assert response.status_code == 401
        assert "Invalid or revoked API key" in response.json()["detail"]

    def test_validate_endpoint_with_api_key(self, client, reset_limits, no_rate_limit):
        """Test /api/validate endpoint with API key authentication."""
        # Use the same key manager that the API uses
        from email_validator_tool.key_manager import create_key_manager
        key_manager = create_key_manager()
        
        # Create a valid API key
        api_key = key_manager.create_key("user")

        # First, get a JWT token using the API key
        token_response = client.post("/api/token", json={"api_key": api_key.key})
        assert token_response.status_code == 200
        
        jwt_token = token_response.json()["access_token"]

        # Make request to validate endpoint
        response = client.post(
            "/api/validate", 
            json={"emails": ["test@example.com"]}, 
            headers={"Authorization": f"Bearer {jwt_token}"}
        )
        
        # Should succeed
        assert response.status_code == 200
        assert "results" in response.json()

    def test_validate_endpoint_with_revoked_api_key(self, client, no_rate_limit):
        """Test /api/validate endpoint with revoked API key returns 401."""
        from email_validator_tool.key_manager import create_key_manager
        key_manager = create_key_manager()
        
        # Create and revoke an API key
        api_key = key_manager.create_key("user")
        key_manager.revoke_key(api_key.key)
        
        # Try to get a JWT token with revoked key - should fail
        token_response = client.post("/api/token", json={"api_key": api_key.key})
        assert token_response.status_code == 401
        assert "Invalid or revoked API key" in token_response.json()["detail"]
        
        # Try to use the revoked key directly in Authorization header
        response = client.post(
            "/api/validate", 
            json={"emails": ["test@example.com"]}, 
            headers={"Authorization": f"Bearer {api_key.key}"}
        )
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]

    def test_admin_endpoint_with_user_api_key(self, client, reset_limits, no_rate_limit):
        """Test admin endpoint with user API key returns 403."""
        # Use the same key manager that the API uses
        from email_validator_tool.key_manager import create_key_manager
        key_manager = create_key_manager()
        
        # Create a user API key
        api_key = key_manager.create_key("user")

        # First, get a JWT token using the API key
        token_response = client.post("/api/token", json={"api_key": api_key.key})
        assert token_response.status_code == 200
        
        jwt_token = token_response.json()["access_token"]

        # Make request to admin endpoint
        response = client.get("/api/cache-stats", headers={"Authorization": f"Bearer {jwt_token}"})

        # Should be forbidden
        assert response.status_code == 403
        # Expect detail message about required admin role
        assert "role" in response.json()["detail"].lower()
        assert "admin" in response.json()["detail"].lower()
        assert "required" in response.json()["detail"].lower()

    def test_admin_endpoint_with_admin_api_key(self, client, reset_limits, no_rate_limit):
        """Test admin endpoint with admin API key succeeds."""
        # Use the same key manager that the API uses
        from email_validator_tool.key_manager import create_key_manager
        key_manager = create_key_manager()
        
        # Create an admin API key
        api_key = key_manager.create_key("admin")

        # First, get a JWT token using the API key
        token_response = client.post("/api/token", json={"api_key": api_key.key})
        assert token_response.status_code == 200
        
        jwt_token = token_response.json()["access_token"]

        # Make request to admin endpoint
        response = client.get("/api/cache-stats", headers={"Authorization": f"Bearer {jwt_token}"})
        
        # Should succeed
        assert response.status_code == 200
        assert "cache_stats" in response.json()

    def test_admin_endpoint_with_revoked_admin_api_key(self, client, no_rate_limit):
        """Test admin endpoint with revoked admin API key returns 401."""
        from email_validator_tool.key_manager import create_key_manager
        key_manager = create_key_manager()
        
        # Create and revoke an admin API key
        api_key = key_manager.create_key("admin")
        key_manager.revoke_key(api_key.key)
        
        # Try to get a JWT token with revoked key - should fail
        token_response = client.post("/api/token", json={"api_key": api_key.key})
        assert token_response.status_code == 401
        assert "Invalid or revoked API key" in token_response.json()["detail"]

    def test_admin_api_key_works_for_admin_endpoints(self, client, setup_test_api_keys, reset_limits, no_rate_limit):
        """Test that admin API key works for admin endpoints."""
        # Get a JWT token using the test admin API key
        token_response = client.post("/api/token", json={"api_key": "test_admin_api_key"})
        assert token_response.status_code == 200
        
        jwt_token = token_response.json()["access_token"]

        # Test admin endpoint
        response = client.get("/api/cache-stats", headers={"Authorization": f"Bearer {jwt_token}"})
        assert response.status_code == 200
        assert "cache_stats" in response.json()

    def test_jwt_token_still_works(self, client, reset_limits, no_rate_limit):
        """Test that JWT tokens created from API keys still work."""
        from email_validator_tool.key_manager import create_key_manager
        key_manager = create_key_manager()
        
        # Create an API key
        api_key = key_manager.create_key("user")

        # Get a JWT token
        token_response = client.post("/api/token", json={"api_key": api_key.key})
        assert token_response.status_code == 200
        
        jwt_token = token_response.json()["access_token"]

        # Test JWT token with retry logic for rate limiting
        response = client.post(
            "/api/validate", 
            json={"emails": ["test@example.com"]}, 
            headers={"Authorization": f"Bearer {jwt_token}"}
        )
        
        # Should succeed
        assert response.status_code == 200
        assert "results" in response.json()
