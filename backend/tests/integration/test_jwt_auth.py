"""
Tests for JWT authentication system.
"""

import time
from datetime import datetime, timedelta, timezone

import pytest
from app.main import app
from email_validator_tool.config import get_settings
from fastapi.testclient import TestClient
from jose import jwt


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def settings():
    return get_settings()


@pytest.fixture
def setup_test_api_keys():
    """Set up test API keys in the key manager."""
    from email_validator_tool.key_manager import create_key_manager

    key_manager = create_key_manager()

    # Create test API keys with known values
    test_user_key = "test_user_api_key"
    test_admin_key = "test_admin_api_key"

    # Create keys if they don't exist
    if not key_manager.validate_key(test_user_key):
        # Create a user key and replace it with our test key
        user_key = key_manager.create_key("user")
        key_manager.keys[test_user_key] = key_manager.keys.pop(user_key.key)
        key_manager.keys[test_user_key].key = test_user_key
        key_manager._save_keys()

    if not key_manager.validate_key(test_admin_key):
        # Create an admin key and replace it with our test key
        admin_key = key_manager.create_key("admin")
        key_manager.keys[test_admin_key] = key_manager.keys.pop(admin_key.key)
        key_manager.keys[test_admin_key].key = test_admin_key
        key_manager._save_keys()

    return key_manager


def get_token_safely(client, api_key, max_retries=3):
    """Safely get a JWT token, handling rate limiting."""
    for attempt in range(max_retries):
        response = client.post("/api/token", json={"api_key": api_key})

        if response.status_code == 200:
            return response.json()["access_token"]
        elif response.status_code == 429:  # Rate limited
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait 1 second before retry
                continue
            else:
                pytest.skip("Rate limited after retries")
        else:
            pytest.fail(f"Token request failed with status {response.status_code}: {response.text}")

    pytest.fail("Failed to get token after all retries")


class TestTokenEndpoint:
    """Test the /api/token endpoint."""

    def test_create_token_with_valid_user_api_key(self, client, settings, setup_test_api_keys, reset_limits):
        """Test creating a JWT token with valid user API key."""
        response = client.post("/api/token", json={"api_key": "test_user_api_key"})

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "user"

        # Verify the token is valid
        token = data["access_token"]
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert payload["role"] == "user"
        assert payload["sub"] == "user_user"

    def test_create_token_with_valid_admin_api_key(self, client, settings, setup_test_api_keys, reset_limits):
        """Test creating a JWT token with valid admin API key."""
        response = client.post("/api/token", json={"api_key": "test_admin_api_key"})

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "admin"

        # Verify the token is valid
        token = data["access_token"]
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert payload["role"] == "admin"
        assert payload["sub"] == "admin_user"

    def test_create_token_with_invalid_api_key(self, client):
        """Test creating a JWT token with invalid API key."""
        response = client.post("/api/token", json={"api_key": "invalid_key"})

        assert response.status_code == 401
        assert "Invalid or revoked API key" in response.json()["detail"]

    def test_create_token_without_api_key(self, client):
        """Test creating a JWT token without API key."""
        response = client.post("/api/token", json={})

        assert response.status_code == 422  # Validation error

    def test_token_rate_limiting(self, client, settings, setup_test_api_keys):
        """Test rate limiting on token endpoint."""
        # Make 101 requests (limit is 100/minute)
        responses = []
        for i in range(101):
            response = client.post("/api/token", json={"api_key": "test_user_api_key"})
            responses.append(response)

        # Check that at least one request was rate limited
        status_codes = [r.status_code for r in responses]
        assert 429 in status_codes


class TestJWTValidation:
    """Test JWT token validation."""

    def test_validate_emails_with_jwt_token(self, client, settings, setup_test_api_keys, reset_limits):
        """Test email validation with JWT token."""
        # First, get a JWT token
        token = get_token_safely(client, "test_user_api_key")

        # Use the JWT token for validation
        response = client.post(
            "/api/validate",
            json={
                "emails": ["test@example.com"],
                "enable_smtp": False,
                "enable_catch_all": False,
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "results" in data

    def test_validate_emails_with_expired_token(self, client, settings):
        """Test email validation with expired JWT token."""
        # Create an expired token
        payload = {
            "sub": "test_user",
            "role": "user",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),  # Expired 1 minute ago
        }
        expired_token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

        response = client.post(
            "/api/validate",
            json={
                "emails": ["test@example.com"],
                "enable_smtp": False,
                "enable_catch_all": False,
            },
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        assert response.status_code == 401

        error_detail = response.json()["detail"].lower()
        assert "invalid token" in error_detail

    def test_validate_emails_with_invalid_token(self, client):
        """Test email validation with invalid JWT token."""
        response = client.post(
            "/api/validate",
            json={
                "emails": ["test@example.com"],
                "enable_smtp": False,
                "enable_catch_all": False,
            },
            headers={"Authorization": "Bearer invalid_token"},
        )

        assert response.status_code == 401

        error_detail = response.json()["detail"].lower()
        assert "invalid token" in error_detail


class TestRoleBasedAccess:
    """Test role-based access control."""

    def test_admin_endpoint_with_user_role(self, client, settings, setup_test_api_keys, reset_limits):
        """Test admin endpoint with user role JWT token."""
        # Get a user JWT token
        token = get_token_safely(client, "test_user_api_key")

        # Try to access admin endpoint
        response = client.get("/api/cache-stats", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 403
        detail = response.json()["detail"].lower()
        assert "role" in detail and "admin" in detail and "required" in detail

    def test_admin_endpoint_with_admin_role(self, client, settings, setup_test_api_keys, reset_limits):
        """Test admin endpoint with admin role JWT token."""
        # Get an admin JWT token
        token = get_token_safely(client, "test_admin_api_key")

        # Access admin endpoint
        response = client.get("/api/cache-stats", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        data = response.json()
        assert "cache_stats" in data

    def test_user_endpoint_with_admin_role(self, client, settings, setup_test_api_keys, reset_limits):
        """Test user endpoint with admin role JWT token."""
        # Get an admin JWT token
        token = get_token_safely(client, "test_admin_api_key")

        # Access user endpoint (should work)
        response = client.post(
            "/api/validate",
            json={
                "emails": ["test@example.com"],
                "enable_smtp": False,
                "enable_catch_all": False,
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200


class TestTokenExpiration:
    """Test token expiration handling."""

    def test_token_expiration_time(self, client, settings, setup_test_api_keys, reset_limits):
        """Test that JWT tokens have the correct expiration time."""
        # Get a token
        token = get_token_safely(client, "test_user_api_key")

        # Decode the token to check expiration
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

        # Check that the token has an expiration claim
        assert "exp" in payload

        # Check that the expiration is reasonable (within 1 hour)
        now = datetime.now(timezone.utc)
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

        # Token should expire in approximately 60 minutes (with some tolerance)
        time_diff = exp_time - now
        assert 3500 <= time_diff.total_seconds() <= 3700  # 58-62 minutes
