from unittest.mock import MagicMock, patch

import pytest
from app.main import app
from app.metrics import (
    add_start_time_middleware,
    create_instrumentator,
    increment_emails_validated,
    record_batch_size,
    set_smtp_connections,
)
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    return TestClient(app)


class TestMetricsEndpoint:
    """Test the /metrics endpoint with IP allowlist"""

    def test_metrics_endpoint_allowed_ip(self, client):
        """Test metrics endpoint allows requests from allowed IPs"""
        with patch("app.main.os.getenv", return_value="127.0.0.1,::1"):
            response = client.get("/metrics")
            assert response.status_code == 200
            # Should contain Prometheus metrics
            assert "emails_validated_total" in response.text

    def test_metrics_endpoint_denied_ip(self, client):
        """Test metrics endpoint denies requests from non-allowed IPs"""
        with patch("app.main.os.getenv", return_value="10.0.0.1"):
            # Mock the request client host to be different from allowed
            with patch("app.main.Request") as mock_request:
                mock_request.return_value.client.host = "192.168.1.1"
                response = client.get("/metrics")
                assert response.status_code == 403
                assert "Access denied" in response.json()["detail"]

    def test_metrics_endpoint_invalid_ip_in_allowlist(self, client):
        """Test metrics endpoint handles invalid IPs in allowlist gracefully"""
        with patch("app.main.os.getenv", return_value="127.0.0.1,invalid-ip,::1"):
            response = client.get("/metrics")
            assert response.status_code == 200

    def test_metrics_endpoint_default_allowlist(self, client):
        """Test metrics endpoint uses default allowlist when env var not set"""
        with patch("app.main.os.getenv", return_value=None):
            # Mock the request client host to be in the default allowlist
            with patch("app.main.Request") as mock_request:
                mock_request.return_value.client.host = "127.0.0.1"
                response = client.get("/metrics")
                assert response.status_code == 200


class TestCustomMetrics:
    """Test custom metrics functions"""

    def test_increment_emails_validated(self):
        """Test incrementing email validation counter"""
        # This should not raise any exceptions
        increment_emails_validated("valid", "org123", 5)
        increment_emails_validated("invalid", "org456", 1)

    def test_set_smtp_connections(self):
        """Test setting SMTP connections gauge"""
        # This should not raise any exceptions
        set_smtp_connections("gmail.com", 10)
        set_smtp_connections("yahoo.com", 5)

    def test_record_batch_size(self):
        """Test recording validation batch size"""
        # This should not raise any exceptions
        record_batch_size("org123", 100)
        record_batch_size("org456", 500)


class TestInstrumentator:
    """Test Prometheus instrumentator configuration"""

    def test_create_instrumentator(self):
        """Test instrumentator creation"""
        instrumentator = create_instrumentator()
        assert instrumentator is not None
        # Check that it has the expected configuration
        assert instrumentator.should_ignore_untemplated is True
        assert instrumentator.should_respect_env_var is True
        assert instrumentator.should_instrument_requests_inprogress is True


class TestMiddleware:
    """Test timing middleware"""

    @pytest.mark.asyncio
    async def test_add_start_time_middleware(self):
        """Test that middleware adds start_time to request state"""
        # Create a mock request
        request = MagicMock()
        request.state = MagicMock()

        # Create a mock call_next function
        async def mock_call_next(req):
            return MagicMock()

        # Call the middleware
        await add_start_time_middleware(request, mock_call_next)

        # Check that start_time was added to request state
        assert hasattr(request.state, "start_time")
        assert isinstance(request.state.start_time, float)


class TestMetricsIntegration:
    """Test metrics integration with validation endpoint"""

    def test_validation_endpoint_records_metrics(self, client):
        """Test that validation endpoint records metrics"""
        # Mock authentication
        with patch("app.api.routes.get_current_user_with_key_manager") as mock_auth:
            mock_auth.return_value = {"organization_id": "test-org-123", "is_database_user": True, "user_id": 1}

            # Mock database session
            with patch("app.api.routes.get_session") as mock_session:
                mock_session.return_value = iter([MagicMock()])

                # Mock user query
                mock_user = MagicMock()
                mock_user.organization_id = "test-org-123"
                mock_session.return_value.__next__().exec.return_value.first.return_value = mock_user

                # Mock validator service
                with patch("app.api.routes.EmailValidatorService") as mock_validator:
                    mock_service = MagicMock()
                    mock_service.validate_many.return_value = [
                        MagicMock(status="valid"),
                        MagicMock(status="invalid"),
                    ]
                    mock_validator.return_value = mock_service

                    # Make request
                    response = client.post(
                        "/api/validate",
                        json={
                            "emails": ["test@example.com", "invalid@example.com"],
                            "enable_smtp": False,
                            "enable_catch_all": False,
                        },
                    )

                    assert response.status_code == 200
                    # The metrics should have been recorded (we can't easily test this without
                    # accessing the actual Prometheus registry, but the code should execute)


class TestMetricsEnvironment:
    """Test metrics environment configuration"""

    def test_metrics_enabled_by_default(self, client):
        """Test that metrics are enabled by default"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_metrics_instrumentation_applied(self, client):
        """Test that metrics instrumentation is applied to the app"""
        # Check that the instrumentator is attached to the app
        assert hasattr(app.state, "instrumentator")
        assert app.state.instrumentator is not None
