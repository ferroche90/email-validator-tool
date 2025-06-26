"""
Unit tests for the key manager functionality.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from cryptography.fernet import Fernet
from email_validator_tool.key_manager import APIKey, KeyManager, create_key_manager


class TestAPIKey:
    """Test APIKey class functionality."""

    def test_api_key_creation(self):
        """Test API key creation with default values."""
        key = "test_key_123"
        role = "user"
        api_key = APIKey(key=key, role=role)

        assert api_key.key == key
        assert api_key.role == role
        assert api_key.revoked is False
        assert api_key.created_at is not None

    def test_api_key_creation_with_custom_values(self):
        """Test API key creation with custom values."""
        from datetime import datetime, timezone

        key = "test_key_456"
        role = "admin"
        created_at = datetime.now(timezone.utc)
        revoked = True

        api_key = APIKey(key=key, role=role, created_at=created_at, revoked=revoked)

        assert api_key.key == key
        assert api_key.role == role
        assert api_key.created_at == created_at
        assert api_key.revoked == revoked

    def test_api_key_to_dict(self):
        """Test API key serialization to dictionary."""
        from datetime import datetime, timezone

        created_at = datetime.now(timezone.utc)
        api_key = APIKey(key="test_key", role="user", created_at=created_at, revoked=False)

        data = api_key.to_dict()

        assert data["key"] == "test_key"
        assert data["role"] == "user"
        assert data["created_at"] == created_at.isoformat()
        assert data["revoked"] is False

    def test_api_key_from_dict(self):
        """Test API key deserialization from dictionary."""
        from datetime import datetime, timezone

        created_at = datetime.now(timezone.utc)
        data = {"key": "test_key", "role": "admin", "created_at": created_at.isoformat(), "revoked": True}

        api_key = APIKey.from_dict(data)

        assert api_key.key == "test_key"
        assert api_key.role == "admin"
        assert api_key.created_at == created_at
        assert api_key.revoked is True


class TestKeyManager:
    """Test KeyManager class functionality."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary data directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def key_manager(self, temp_data_dir):
        """Create a KeyManager instance for testing."""
        return KeyManager(data_dir=temp_data_dir)

    def test_key_manager_initialization(self, temp_data_dir):
        """Test KeyManager initialization."""
        key_manager = KeyManager(data_dir=temp_data_dir)

        assert key_manager.data_dir == Path(temp_data_dir)
        assert key_manager.keys_file == Path(temp_data_dir) / "api_keys.json"
        assert key_manager.encryption_key_file == Path(temp_data_dir) / ".encryption_key"
        assert isinstance(key_manager.fernet, Fernet)
        assert len(key_manager.keys) == 0

    def test_create_key_user(self, key_manager):
        """Test creating a user API key."""
        api_key = key_manager.create_key("user")

        assert api_key.role == "user"
        assert api_key.revoked is False
        assert len(api_key.key) > 0
        assert api_key.key in key_manager.keys

    def test_create_key_admin(self, key_manager):
        """Test creating an admin API key."""
        api_key = key_manager.create_key("admin")

        assert api_key.role == "admin"
        assert api_key.revoked is False
        assert len(api_key.key) > 0
        assert api_key.key in key_manager.keys

    def test_create_key_invalid_role(self, key_manager):
        """Test creating an API key with invalid role."""
        with pytest.raises(ValueError, match="Role must be 'user' or 'admin'"):
            key_manager.create_key("invalid_role")

    def test_list_keys_empty(self, key_manager):
        """Test listing keys when no keys exist."""
        keys = key_manager.list_keys()
        assert len(keys) == 0

    def test_list_keys_with_keys(self, key_manager):
        """Test listing keys when keys exist."""
        # Create some keys
        _user_key = key_manager.create_key("user")
        _admin_key = key_manager.create_key("admin")

        keys = key_manager.list_keys()
        assert len(keys) == 2

        # Check that both keys are in the list
        key_roles = [key.role for key in keys]
        assert "user" in key_roles
        assert "admin" in key_roles

    def test_revoke_key(self, key_manager):
        """Test revoking an API key."""
        api_key = key_manager.create_key("user")

        # Verify key is not revoked initially
        assert not key_manager.keys[api_key.key].revoked

        # Revoke the key
        result = key_manager.revoke_key(api_key.key)
        assert result is True

        # Verify key is now revoked
        assert key_manager.keys[api_key.key].revoked

    def test_revoke_nonexistent_key(self, key_manager):
        """Test revoking a key that doesn't exist."""
        result = key_manager.revoke_key("nonexistent_key")
        assert result is False

    def test_validate_key_active(self, key_manager):
        """Test validating an active API key."""
        api_key = key_manager.create_key("admin")

        role = key_manager.validate_key(api_key.key)
        assert role == "admin"

    def test_validate_key_revoked(self, key_manager):
        """Test validating a revoked API key."""
        api_key = key_manager.create_key("user")

        # Revoke the key
        key_manager.revoke_key(api_key.key)

        # Try to validate the revoked key
        role = key_manager.validate_key(api_key.key)
        assert role is None

    def test_validate_nonexistent_key(self, key_manager):
        """Test validating a key that doesn't exist."""
        role = key_manager.validate_key("nonexistent_key")
        assert role is None

    def test_get_key_info(self, key_manager):
        """Test getting key information."""
        api_key = key_manager.create_key("user")

        key_info = key_manager.get_key_info(api_key.key)
        assert key_info is not None
        assert key_info.key == api_key.key
        assert key_info.role == "user"

    def test_get_nonexistent_key_info(self, key_manager):
        """Test getting information for a key that doesn't exist."""
        key_info = key_manager.get_key_info("nonexistent_key")
        assert key_info is None

    def test_persistence(self, temp_data_dir):
        """Test that keys are persisted and can be reloaded."""
        # Create first key manager and add a key
        key_manager1 = KeyManager(data_dir=temp_data_dir)
        api_key = key_manager1.create_key("admin")

        # Create second key manager (should load existing keys)
        key_manager2 = KeyManager(data_dir=temp_data_dir)

        # Verify the key exists in the second manager
        assert api_key.key in key_manager2.keys
        assert key_manager2.keys[api_key.key].role == "admin"
        assert key_manager2.keys[api_key.key].revoked is False

    def test_persistence_with_revoked_key(self, temp_data_dir):
        """Test that revoked keys are persisted correctly."""
        # Create first key manager, add a key, and revoke it
        key_manager1 = KeyManager(data_dir=temp_data_dir)
        api_key = key_manager1.create_key("user")
        key_manager1.revoke_key(api_key.key)

        # Create second key manager
        key_manager2 = KeyManager(data_dir=temp_data_dir)

        # Verify the key is revoked in the second manager
        assert api_key.key in key_manager2.keys
        assert key_manager2.keys[api_key.key].revoked is True

        # Verify validation fails
        role = key_manager2.validate_key(api_key.key)
        assert role is None


class TestCreateKeyManager:
    """Test create_key_manager function."""

    def test_create_key_manager(self):
        """Test create_key_manager function."""
        key_manager = create_key_manager()
        assert isinstance(key_manager, KeyManager)


class TestCLIIntegration:
    """Test CLI integration with key manager."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary data directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @patch("email_validator_tool.key_manager.KeyManager")
    def test_cli_create_key(self, mock_key_manager_class, temp_data_dir):
        """Test CLI create key command."""
        from email_validator_tool.cli import create

        # Mock the key manager
        mock_key_manager = mock_key_manager_class.return_value
        mock_api_key = APIKey(key="test_key_123", role="user")
        mock_key_manager.create_key.return_value = mock_api_key

        # Mock JWT generation
        with patch("email_validator_tool.cli.generate_jwt_for_key") as mock_jwt:
            mock_jwt.return_value = "jwt_token_123"

            # Test creating a user key
            with patch("typer.echo") as mock_echo:
                create("user")

                # Verify key was created
                mock_key_manager.create_key.assert_called_once_with("user")

                # Verify JWT was generated
                mock_jwt.assert_called_once_with("test_key_123", "user")

                # Verify output was displayed
                assert mock_echo.call_count >= 5  # Multiple echo calls for output

    @patch("email_validator_tool.key_manager.KeyManager")
    def test_cli_list_keys(self, mock_key_manager_class, temp_data_dir):
        """Test CLI list keys command."""
        from email_validator_tool.cli import list as list_keys

        # Mock the key manager
        mock_key_manager = mock_key_manager_class.return_value
        mock_keys = [APIKey(key="key1", role="user", revoked=False), APIKey(key="key2", role="admin", revoked=True)]
        mock_key_manager.list_keys.return_value = mock_keys

        with patch("typer.echo") as mock_echo:
            list_keys()

            # Verify keys were listed
            mock_key_manager.list_keys.assert_called_once()

            # Verify output was displayed
            mock_echo.assert_called()

    @patch("email_validator_tool.key_manager.KeyManager")
    def test_cli_revoke_key(self, mock_key_manager_class, temp_data_dir):
        """Test CLI revoke key command."""
        from email_validator_tool.cli import revoke

        # Mock the key manager
        mock_key_manager = mock_key_manager_class.return_value
        mock_key_manager.keys = {"test_key_123": APIKey(key="test_key_123", role="user")}
        mock_key_manager.revoke_key.return_value = True
        mock_key_manager.get_key_info.return_value = APIKey(key="test_key_123", role="user", revoked=False)

        with patch("typer.echo") as mock_echo:
            revoke("test_key_123")

            # Verify key was revoked
            mock_key_manager.revoke_key.assert_called_once_with("test_key_123")

            # Verify success message was displayed (key is truncated to 16 chars + ...)
            mock_echo.assert_called_with("✅ API key 'test_key_123...' has been revoked.")
