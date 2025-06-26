"""Integration tests for advanced API features."""

from fastapi.testclient import TestClient

from backend.tests.conftest import get_token_safely


def test_validate_emails_unauthorized(client: TestClient):
    """Test that validation endpoint returns 403 without token."""
    response = client.post(
        "/api/validate",
        json={
            "emails": ["test@example.com"],
            "enable_smtp": False,
            "enable_catch_all": False,
        },
    )
    assert response.status_code == 403
    # FastAPI returns "Not authenticated" when no credentials provided
    assert "Not authenticated" in response.json()["detail"]


def test_validate_emails_with_options(client, setup_test_api_keys):
    """Test email validation with various options."""
    # Get a JWT token first
    token = get_token_safely(client, "test_admin_api_key")

    response = client.post(
        "/api/validate",
        json={
            "emails": ["test@example.com"],
            "enable_smtp": True,
            "enable_catch_all": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 1


def test_validate_emails_with_invalid_emails(client, setup_test_api_keys):
    """Test email validation with invalid email addresses."""
    # Get a JWT token first
    token = get_token_safely(client, "test_admin_api_key")

    response = client.post(
        "/api/validate",
        json={
            "emails": ["invalid-email", "another@invalid", "test@example.com"],
            "enable_smtp": False,
            "enable_catch_all": False,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 3

    # Check that invalid emails are marked as such
    invalid_results = [r for r in data["results"] if not r["is_valid"]]
    assert len(invalid_results) >= 2


def test_validate_emails_with_empty_list(client, setup_test_api_keys):
    """Test email validation with empty email list."""
    # Get a JWT token first
    token = get_token_safely(client, "test_admin_api_key")

    response = client.post(
        "/api/validate",
        json={
            "emails": [],
            "enable_smtp": False,
            "enable_catch_all": False,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 0


def test_validate_emails_with_large_list(client, setup_test_api_keys):
    """Test email validation with a large list of emails."""
    # Get a JWT token first
    token = get_token_safely(client, "test_admin_api_key")

    # Create a list of 100 test emails
    emails = [f"test{i}@example.com" for i in range(100)]

    response = client.post(
        "/api/validate",
        json={
            "emails": emails,
            "enable_smtp": False,
            "enable_catch_all": False,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 100


def test_rate_limit_exceeded(client, setup_test_api_keys):
    """Test rate limiting by making requests quickly."""
    # Get a JWT token first
    token = get_token_safely(client, "test_admin_api_key")

    # Make 21 requests to trigger rate limit (20/minute limit)
    responses = []
    for i in range(21):
        response = client.post(
            "/api/validate",
            json={
                "emails": [f"test{i}@example.com"],
                "enable_smtp": False,
                "enable_catch_all": False,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        responses.append(response)

    # Check that at least one request was rate limited
    status_codes = [r.status_code for r in responses]
    assert 429 in status_codes, f"Expected 429 in status codes: {status_codes}"


def test_admin_endpoints_unauthorized(client: TestClient):
    """Test admin endpoints return 403 without admin token."""
    # Test cache-stats
    response = client.get("/api/cache-stats")
    assert response.status_code == 403

    # Test cache-clear
    response = client.post("/api/cache-clear")
    assert response.status_code == 403

    # Test bounce-stats
    response = client.get("/api/bounce-stats")
    assert response.status_code == 403


def test_admin_endpoints_require_admin_role(client, setup_test_api_keys):
    """Test that admin endpoints require admin role."""
    # Get a user token (not admin)
    user_token = get_token_safely(client, "test_user_api_key")

    # Try to access admin endpoint with user token
    response = client.get("/api/cache-stats", headers={"Authorization": f"Bearer {user_token}"})

    # Should be forbidden
    assert response.status_code == 403


def test_cache_stats_endpoint(client, setup_test_api_keys):
    """Test the cache stats endpoint."""
    # Get a JWT token first
    token = get_token_safely(client, "test_admin_api_key")

    response = client.get("/api/cache-stats", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert "cache_stats" in data


def test_cache_clear_endpoint(client, setup_test_api_keys):
    """Test the cache clear endpoint."""
    # Get a JWT token first
    token = get_token_safely(client, "test_admin_api_key")

    response = client.post("/api/cache-clear", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_bounce_stats_endpoint(client, setup_test_api_keys):
    """Test the bounce stats endpoint."""
    # Get a JWT token first
    token = get_token_safely(client, "test_admin_api_key")

    response = client.get("/api/bounce-stats", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert "bounce_stats" in data


def test_health_endpoint(client: TestClient):
    """Test the health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
