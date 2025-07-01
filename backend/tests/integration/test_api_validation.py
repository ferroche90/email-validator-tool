"""Integration tests for email validation API."""

from fastapi.testclient import TestClient

from backend.tests.conftest import get_token_safely


def test_validate_emails(client: TestClient, setup_test_api_keys, reset_limits, no_rate_limit):
    """Test the /validate endpoint with authentication"""
    # Get a real JWT token first
    token = get_token_safely(client, "test_admin_api_key")
    
    # Test data
    test_data = {
        "emails": ["hello@example.com"],
        "enable_smtp": False,
        "enable_catch_all": False,
    }

    # Make request with real Bearer token
    response = client.post(
        "/api/validate",
        json=test_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    # Should succeed
    assert response.status_code == 200
    response_data = response.json()
    assert "results" in response_data

    # Check that results contain validation status
    results = response_data["results"]
    assert len(results) == 1
    assert "status" in results[0]
    assert "email" in results[0]


def test_validate_emails_endpoint(client, setup_test_api_keys, reset_limits, no_rate_limit):
    """Test the /api/validate endpoint."""
    # Get a JWT token first
    token = get_token_safely(client, "test_admin_api_key")

    response = client.post(
        "/api/validate",
        json={
            "emails": ["test@example.com", "invalid-email", "another@example.com"],
            "enable_smtp": False,
            "enable_catch_all": False,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    
    # Should succeed
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 3
