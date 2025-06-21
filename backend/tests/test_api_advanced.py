import pytest
import time
from fastapi.testclient import TestClient

def test_validate_emails_unauthorized(client: TestClient):
    """Test that validation endpoint returns 401 without token."""
    response = client.post(
        "/api/validate",
        json={
            "emails": ["test@example.com"],
            "enable_smtp": False,
            "enable_catch_all": False
        }
    )
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

def test_validate_emails_success(client: TestClient):
    """Test successful email validation with valid token."""
    response = client.post(
        "/api/validate",
        json={
            "emails": ["test@example.com"],
            "enable_smtp": False,
            "enable_catch_all": False
        },
        headers={"Authorization": "Bearer YOUR_TOKEN_HERE"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 1
    assert "email" in data["results"][0]
    assert "status" in data["results"][0]

def test_validate_emails_invalid_email(client: TestClient):
    """Test validation with invalid email format."""
    response = client.post(
        "/api/validate",
        json={
            "emails": ["invalid-email"],
            "enable_smtp": False,
            "enable_catch_all": False
        },
        headers={"Authorization": "Bearer YOUR_TOKEN_HERE"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 1
    # Should return invalid status
    assert data["results"][0]["status"] in ["invalid_syntax", "invalid_domain"]

def test_validate_emails_multiple_emails(client: TestClient):
    """Test validation with multiple emails."""
    response = client.post(
        "/api/validate",
        json={
            "emails": ["test@example.com", "admin@example.com", "invalid-email"],
            "enable_smtp": False,
            "enable_catch_all": False
        },
        headers={"Authorization": "Bearer YOUR_TOKEN_HERE"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 3

def test_rate_limit_exceeded(client: TestClient):
    """Test rate limiting by making 25 requests quickly."""
    # Make 25 requests to trigger rate limit (20/minute limit)
    responses = []
    for i in range(25):
        response = client.post(
            "/api/validate",
            json={
                "emails": [f"test{i}@example.com"],
                "enable_smtp": False,
                "enable_catch_all": False
            },
            headers={"Authorization": "Bearer YOUR_TOKEN_HERE"}
        )
        responses.append(response)
    
    # Check that at least one request was rate limited
    status_codes = [r.status_code for r in responses]
    assert 429 in status_codes, f"Expected 429 in status codes: {status_codes}"

def test_admin_endpoints_unauthorized(client: TestClient):
    """Test admin endpoints return 403 without admin token."""
    # Test cache-stats
    response = client.get("/api/cache-stats")
    assert response.status_code == 401
    
    # Test cache-clear
    response = client.post("/api/cache-clear")
    assert response.status_code == 401
    
    # Test bounce-stats
    response = client.get("/api/bounce-stats")
    assert response.status_code == 401

def test_admin_endpoints_with_regular_token(client: TestClient):
    """Test admin endpoints return 403 with regular token."""
    # Test cache-stats
    response = client.get(
        "/api/cache-stats",
        headers={"Authorization": "Bearer YOUR_TOKEN_HERE"}
    )
    assert response.status_code == 403
    
    # Test cache-clear
    response = client.post(
        "/api/cache-clear",
        headers={"Authorization": "Bearer YOUR_TOKEN_HERE"}
    )
    assert response.status_code == 403
    
    # Test bounce-stats
    response = client.get(
        "/api/bounce-stats",
        headers={"Authorization": "Bearer YOUR_TOKEN_HERE"}
    )
    assert response.status_code == 403

def test_admin_endpoints_success(client: TestClient):
    """Test admin endpoints with admin token."""
    # Test cache-stats
    response = client.get(
        "/api/cache-stats",
        headers={"Authorization": "Bearer admin_token_here"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "cache_stats" in data
    assert "cache_enabled" in data
    
    # Test cache-clear
    response = client.post(
        "/api/cache-clear",
        headers={"Authorization": "Bearer admin_token_here"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "cleared" in data
    assert "message" in data
    
    # Test bounce-stats
    response = client.get(
        "/api/bounce-stats",
        headers={"Authorization": "Bearer admin_token_here"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "bounce_count" in data
    assert "loaded_in_memory" in data

def test_health_endpoint(client: TestClient):
    """Test the health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"} 