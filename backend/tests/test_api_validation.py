import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_validate_emails():
    """Test the /validate endpoint with authentication"""
    # Test data
    test_data = {
        "emails": ["hello@example.com"],
        "enable_smtp": False,
        "enable_catch_all": False
    }
    
    # Make request with Bearer token
    response = client.post(
        "/api/validate",
        json=test_data,
        headers={"Authorization": "Bearer YOUR_TOKEN_HERE"}
    )
    
    # Assert response
    assert response.status_code == 200
    response_data = response.json()
    assert "results" in response_data
    
    # Check that results contain validation status
    results = response_data["results"]
    assert len(results) == 1
    assert "status" in results[0]
    assert "email" in results[0] 