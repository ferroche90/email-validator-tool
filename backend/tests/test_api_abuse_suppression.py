"""Integration tests for abuse and suppression endpoints."""

import pytest
from fastapi.testclient import TestClient

from .conftest import get_token_safely


def test_add_suppressions_endpoint(client, setup_test_api_keys):
    """Test the /api/admin/suppressions endpoint."""
    # Get admin token
    token = get_token_safely(client, "test_admin_api_key")
    
    # Test adding suppressions
    response = client.post(
        "/api/admin/suppressions",
        json={"emails": ["test@suppression.com", "another@suppression.com"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "added_count" in data
    assert "total_suppressions" in data
    assert data["added_count"] >= 0


def test_add_suppressions_unauthorized(client):
    """Test that suppression endpoint requires admin access."""
    response = client.post(
        "/api/admin/suppressions",
        json={"emails": ["test@suppression.com"]},
    )
    assert response.status_code == 403


def test_suppression_stats_endpoint(client, setup_test_api_keys):
    """Test the /api/admin/suppression-stats endpoint."""
    # Get admin token
    token = get_token_safely(client, "test_admin_api_key")
    
    response = client.get(
        "/api/admin/suppression-stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "suppression_count" in data
    assert "loaded_in_memory" in data
    assert data["loaded_in_memory"] is True


def test_abuse_stats_endpoint(client, setup_test_api_keys):
    """Test the /api/admin/abuse-stats endpoint."""
    # Get admin token
    token = get_token_safely(client, "test_admin_api_key")
    
    response = client.get(
        "/api/admin/abuse-stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "abuse_count" in data
    assert "loaded_in_memory" in data
    assert data["loaded_in_memory"] is True


def test_validate_with_abuse_and_suppression(client, setup_test_api_keys):
    """Test that validation includes abuse and suppression checks."""
    # Get admin token
    token = get_token_safely(client, "test_admin_api_key")
    
    # First add a suppression
    client.post(
        "/api/admin/suppressions",
        json={"emails": ["test@suppression.com"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    
    # Test validation with abuse and suppressed emails
    response = client.post(
        "/api/validate",
        json={
            "emails": [
                "abuse@example.com",  # Should be ABUSE
                "test@suppression.com",  # Should be SUPPRESSED
                "john.doe@example.com",  # Should be VALID
            ],
            "enable_smtp": False,
            "enable_catch_all": False,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 3
    
    # Check that we have the expected statuses
    statuses = [result["status"] for result in data["results"]]
    assert "abuse" in statuses
    assert "suppressed" in statuses
    assert "valid" in statuses 