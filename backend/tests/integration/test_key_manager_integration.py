"""
Integration tests for key manager functionality.
"""

import tempfile
from pathlib import Path

import pytest
from app.main import app
from email_validator_tool.key_manager import KeyManager
from fastapi.testclient import TestClient

from backend.tests.conftest import get_token_safely


class TestKeyManagerBackendIntegration:
    """Test key manager integration with backend API."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary data directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def key_manager(self, temp_data_dir):
        """Create a key manager for testing."""
        return KeyManager(data_dir=temp_data_dir)

    def test_token_endpoint_with_valid_api_key(self, client, key_manager):
        """Test /api/token endpoint with a valid API key."""
        # Create a valid API key
        api_key = key_manager.create_key("user")

        # Make request to token endpoint
        response = client.post("/api/token", json={"api_key": api_key.key})

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "user"

    def test_token_endpoint_with_revoked_api_key(self, client, key_manager):
        """Test /api/token endpoint with a revoked API key returns 401."""
        # Create and revoke an API key
        api_key = key_manager.create_key("admin")
        key_manager.revoke_key(api_key.key)

        # Make request to token endpoint
        response = client.post("/api/token", json={"api_key": api_key.key})

        assert response.status_code == 401
        assert "Invalid or revoked API key" in response.json()["detail"]

    def test_token_endpoint_with_invalid_api_key(self, client):
        """Test /api/token endpoint with an invalid API key returns 401."""
        # Make request with invalid API key
        response = client.post("/api/token", json={"api_key": "invalid_key_123"})

        assert response.status_code == 401
        assert "Invalid or revoked API key" in response.json()["detail"]

    def test_validate_endpoint_with_api_key(self, client, key_manager):
        """Test /api/validate endpoint with API key authentication."""
        # Create a valid API key
        api_key = key_manager.create_key("user")

        # Make request to validate endpoint
        response = client.post(
            "/api/validate", json={"emails": ["test@example.com"]}, headers={"Authorization": f"Bearer {api_key.key}"}
        )

        assert response.status_code == 200
        assert "results" in response.json()

    def test_validate_endpoint_with_revoked_api_key(self, client, key_manager):
        """Test /api/validate endpoint with revoked API key returns 401."""
        # Create and revoke an API key
        api_key = key_manager.create_key("user")
        key_manager.revoke_key(api_key.key)

        # Make request to validate endpoint
        response = client.post(
            "/api/validate", json={"emails": ["test@example.com"]}, headers={"Authorization": f"Bearer {api_key.key}"}
        )

        assert response.status_code == 401

    def test_admin_endpoint_with_user_api_key(self, client, key_manager):
        """Test admin endpoint with user API key returns 403."""
        # Create a user API key
        api_key = key_manager.create_key("user")

        # Make request to admin endpoint
        response = client.get("/api/cache-stats", headers={"Authorization": f"Bearer {api_key.key}"})

        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    def test_admin_endpoint_with_admin_api_key(self, client, key_manager):
        """Test admin endpoint with admin API key succeeds."""
        # Create an admin API key
        api_key = key_manager.create_key("admin")

        # Make request to admin endpoint
        response = client.get("/api/cache-stats", headers={"Authorization": f"Bearer {api_key.key}"})

        assert response.status_code == 200
        assert "cache_stats" in response.json()

    def test_admin_endpoint_with_revoked_admin_api_key(self, client, key_manager):
        """Test admin endpoint with revoked admin API key returns 401."""
        # Create and revoke an admin API key
        api_key = key_manager.create_key("admin")
        key_manager.revoke_key(api_key.key)

        # Make request to admin endpoint
        response = client.get("/api/cache-stats", headers={"Authorization": f"Bearer {api_key.key}"})

        assert response.status_code == 401

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

        # Test JWT token
        response = client.post(
            "/api/validate", json={"emails": ["test@example.com"]}, headers={"Authorization": f"Bearer {jwt_token}"}
        )
        assert response.status_code == 200
