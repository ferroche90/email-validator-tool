"""
Common test fixtures for email validator tests.

This file also contains several global tweaks to make the whole test-suite
work smoothly when running inside `pytest-asyncio` and with FastAPI.
"""

import os
import time
from unittest.mock import patch
from contextlib import contextmanager

import pytest
from app.main import app, limiter as _global_limiter
from email_validator_tool.core.pipeline import ValidationPipeline
from email_validator_tool.core.results import ValidationResult
from fastapi.testclient import TestClient
from app.api import routes as _routes_module
from app.api.routes import get_current_user_with_key_manager as _orig_get_user
from app.auth.base import require_role as _require_role
import inspect, asyncio
import asyncio as _asyncio

# Set test environment variables to increase rate limits for testing
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"
os.environ["RATE_LIMIT_PER_MINUTE"] = "10000"  # Very high rate limit for tests

# Note: We keep rate limiting enabled so tests that exercise rate limiting behave correctly.

from email_validator_tool.key_manager import create_key_manager
import sqlite3

try:
    import pytest_benchmark.plugin  # type: ignore
    _benchmark_plugin_loaded = True
except ImportError:
    _benchmark_plugin_loaded = False

from sqlmodel.orm.session import Session as _SQLSession
from sqlalchemy import text as _sql_text

# Patch Session.exec once to accept raw SQL strings used in some legacy tests
_orig_exec = _SQLSession.exec

def _exec_with_text(self, statement, *args, **kwargs):
    if isinstance(statement, str):
        statement = _sql_text(statement)
    return _orig_exec(self, statement, *args, **kwargs)

_SQLSession.exec = _exec_with_text

# Store original rate limit functions
_original_rate_limit_functions = {}

@contextmanager
def disable_rate_limiting():
    """Context manager to temporarily disable rate limiting for tests."""
    # Store originals so we can restore later
    original_limit = _global_limiter.limit
    original_enabled_state = getattr(_global_limiter, "enabled", None)

    try:
        # Replace with a no-op decorator so any **newly declared** routes inside tests are unaffected
        def no_limit(*args, **kwargs):
            def decorator(func):
                return func
            return decorator

        _global_limiter.limit = no_limit

        # Completely disable the limiter for **already decorated** routes by flipping the
        # internal `enabled` flag if it exists (SlowAPI exposes this attribute).
        if original_enabled_state is not None:
            _global_limiter.enabled = False
        yield
    finally:
        # Restore original method
        _global_limiter.limit = original_limit
        if original_enabled_state is not None:
            _global_limiter.enabled = original_enabled_state

@contextmanager
def reset_rate_limit_counters():
    """Context manager to reset rate limit counters between tests."""
    try:
        # Clear the rate limit storage
        if hasattr(_global_limiter, 'storage'):
            _global_limiter.storage.clear()
        yield
    except Exception:
        # If clearing fails, just continue
        yield

@pytest.fixture
def no_rate_limit():
    """Fixture to disable rate limiting for a test."""
    with disable_rate_limiting():
        yield

@pytest.fixture
def reset_limits():
    """Fixture to reset rate limit counters before a test."""
    with reset_rate_limit_counters():
        yield

@pytest.fixture
def high_rate_limit():
    """Fixture to set very high rate limits for a test."""
    # Store original environment
    original_limit = os.environ.get("RATE_LIMIT_PER_MINUTE", "1000")
    
    try:
        # Set very high limits
        os.environ["RATE_LIMIT_PER_MINUTE"] = "100000"
        yield
    finally:
        # Restore original
        os.environ["RATE_LIMIT_PER_MINUTE"] = original_limit

@pytest.fixture
def valid_email():
    """Return a valid email address for testing."""
    return "john.doe@example.com"


@pytest.fixture
def invalid_email():
    """Return an invalid email address for testing."""
    return "invalid@email"


@pytest.fixture
def disposable_email():
    """Return a disposable email address for testing."""
    return "test@mailinator.com"


@pytest.fixture
def role_account_email():
    """Return a role account email address for testing."""
    return "admin@example.com"


@pytest.fixture
def validation_result():
    """Return a ValidationResult instance for testing."""
    return ValidationResult()


@pytest.fixture
def validation_pipeline():
    """Return a ValidationPipeline instance for testing."""
    return ValidationPipeline(enable_smtp=False, enable_catch_all=False)


@pytest.fixture
def client():
    """FastAPI TestClient with overridden settings for testing."""
    with patch("email_validator_tool.config.get_settings") as mock_settings:
        # Override settings for testing
        mock_settings.return_value.ENABLE_DNS_CACHE = False
        mock_settings.return_value.DNS_CACHE_TTL_SECONDS = 0
        mock_settings.return_value.ENABLE_SMTP = False
        mock_settings.return_value.ENABLE_CATCH_ALL = False
        mock_settings.return_value.MAX_CONCURRENT_CONNECTIONS = 1
        mock_settings.return_value.SMTP_TIMEOUT = 1

        with TestClient(app) as test_client:
            # Create the expected API keys in the key manager for testing
            key_manager = create_key_manager()

            # Create test API keys if they don't exist
            # We'll create them with the expected values from settings
            if not key_manager.validate_key("test_user_api_key"):
                # Create a user key with the expected value
                user_key = key_manager.create_key("user")
                # Replace the generated key with our test key
                key_manager.keys["test_user_api_key"] = key_manager.keys.pop(user_key.key)
                key_manager.keys["test_user_api_key"].key = "test_user_api_key"
                key_manager._save_keys()

            if not key_manager.validate_key("test_admin_api_key"):
                # Create an admin key with the expected value
                admin_key = key_manager.create_key("admin")
                # Replace the generated key with our test key
                key_manager.keys["test_admin_api_key"] = key_manager.keys.pop(admin_key.key)
                key_manager.keys["test_admin_api_key"].key = "test_admin_api_key"
                key_manager._save_keys()

            yield test_client


def get_token_safely(client: TestClient, api_key: str, max_retries: int = 3):
    """Safely retrieve a JWT token from the API, retrying if rate limited."""
    for attempt in range(max_retries):
        response = client.post("/api/token", json={"api_key": api_key})

        if response.status_code == 200:
            return response.json()["access_token"]
        elif response.status_code == 429:  # Rate limited
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait 1 second before retrying
                continue
            pytest.skip("Rate limited after retries")
        else:
            pytest.fail(f"Token request failed with status {response.status_code}: {response.text}")

    pytest.fail("Failed to obtain token after all retries")


@pytest.fixture(scope="session")
def setup_test_api_keys():
    """Ensure the well-known test API keys exist and return the key manager instance."""
    key_manager = create_key_manager()

    # Known test keys used across many integration-tests
    predefined = {"test_user_api_key": "user", "test_admin_api_key": "admin"}

    for api_key, role in predefined.items():
        if not key_manager.validate_key(api_key):
            generated = key_manager.create_key(role)
            # Replace generated key entry with our fixed value so tests are deterministic
            key_manager.keys[api_key] = key_manager.keys.pop(generated.key)
            key_manager.keys[api_key].key = api_key
            key_manager._save_keys()

    return key_manager


if not _benchmark_plugin_loaded:
    @pytest.fixture
    def benchmark():
        """Stub benchmark fixture when pytest-benchmark plugin is not available."""

        def _run(func, *args, **kwargs):
            res = func(*args, **kwargs)
            if inspect.iscoroutine(res):
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(res)
            return res

        return _run

_original_asyncio_run = _asyncio.run

def _safe_asyncio_run(main, *args, **kwargs):  # type: ignore
    """A drop-in replacement for `asyncio.run` that works inside an active loop.

    Some unit-tests call `asyncio.run()` even though they are already running
    inside a pytest-managed event-loop (e.g. tests marked with
    ``@pytest.mark.asyncio``).  The vanilla implementation raises
    `RuntimeError` in this scenario.  We detect the nested call and instead use
    ``loop.run_until_complete`` so the test continues to work.
    """

    running_loop = _asyncio.get_running_loop()

    # Prepare the coroutine to execute
    if _asyncio.iscoroutine(main):
        coro = main
    else:
        coro = main(*args, **kwargs)

    import threading
    
    result_holder = {}
    exc_holder = {}

    def _thread_runner():
        try:
            result_holder["value"] = _original_asyncio_run(coro)
        except Exception as e:  # pragma: no cover
            exc_holder["err"] = e

    t = threading.Thread(target=_thread_runner)
    t.start()
    t.join()

    if "err" in exc_holder:
        raise exc_holder["err"]

    return result_holder.get("value")

# Apply monkey-patch once when tests are imported
_asyncio.run = _safe_asyncio_run

# ---------------------------------------------------------------------------
#  Global autouse fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _clear_domain_throttle_state():
    """Reset per-domain throttle storage before each test for isolation."""
    from email_validator_tool.validators import throttle as _throttle

    _throttle._last_contact.clear()
    yield
    _throttle._last_contact.clear()
