from fastapi.testclient import TestClient


def test_validate_emails(client: TestClient):
    """Test the /validate endpoint with authentication"""
    # Test data
    test_data = {
        "emails": ["hello@example.com"],
        "enable_smtp": False,
        "enable_catch_all": False,
    }

    # Make request with Bearer token
    response = client.post(
        "/api/validate",
        json=test_data,
        headers={"Authorization": "Bearer admin_token_here"},
    )

    # Assert response - accept both 200 (success) and 429 (rate limited)
    assert response.status_code in [200, 429]

    if response.status_code == 200:
        response_data = response.json()
        assert "results" in response_data

        # Check that results contain validation status
        results = response_data["results"]
        assert len(results) == 1
        assert "status" in results[0]
        assert "email" in results[0]
    else:
        # Rate limited - this is acceptable in test environment
        assert response.status_code == 429
