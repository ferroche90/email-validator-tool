"""
API Key Management System

Handles creation, storage, and validation of API keys with encrypted persistence.
"""

import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from cryptography.fernet import Fernet
from loguru import logger
from tabulate import tabulate

from email_validator_tool.config import get_settings
from email_validator_tool.utils.paths import get_data_dir


class APIKey:
    """Represents an API key with metadata."""
    
    def __init__(self, key: str, role: str, created_at: Optional[datetime] = None, revoked: bool = False):
        self.key = key
        self.role = role
        self.created_at = created_at or datetime.now(timezone.utc)
        self.revoked = revoked
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "key": self.key,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
            "revoked": self.revoked
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "APIKey":
        """Create from dictionary."""
        return cls(
            key=data["key"],
            role=data["role"],
            created_at=datetime.fromisoformat(data["created_at"]),
            revoked=data.get("revoked", False)
        )


class KeyManager:
    """Manages API keys with encrypted storage."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.keys_file = self.data_dir / "api_keys.json"
        self.encryption_key_file = self.data_dir / ".encryption_key"
        
        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize encryption
        self._init_encryption()
        
        # Load existing keys
        self.keys: Dict[str, APIKey] = {}
        self._load_keys()
    
    def _init_encryption(self):
        """Initialize or load encryption key."""
        if self.encryption_key_file.exists():
            # Load existing key
            with open(self.encryption_key_file, "rb") as f:
                key = f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(self.encryption_key_file, "wb") as f:
                f.write(key)
            logger.info(f"Generated new encryption key: {self.encryption_key_file}")
        
        self.fernet = Fernet(key)
    
    def _load_keys(self):
        """Load keys from encrypted file."""
        if self.keys_file.exists():
            try:
                with open(self.keys_file, "rb") as f:
                    encrypted_data = f.read()
                
                decrypted_data = self.fernet.decrypt(encrypted_data)
                data = json.loads(decrypted_data.decode())
                
                self.keys = {
                    key_id: APIKey.from_dict(key_data)
                    for key_id, key_data in data.items()
                }
                logger.info(f"Loaded {len(self.keys)} API keys")
            except Exception as e:
                logger.error(f"Error loading API keys: {e}")
                self.keys = {}
        else:
            logger.info("No existing API keys found")
    
    def _save_keys(self):
        """Save keys to encrypted file."""
        try:
            data = {
                key_id: key.to_dict()
                for key_id, key in self.keys.items()
            }
            
            json_data = json.dumps(data, indent=2)
            encrypted_data = self.fernet.encrypt(json_data.encode())
            
            with open(self.keys_file, "wb") as f:
                f.write(encrypted_data)
            
            logger.debug(f"Saved {len(self.keys)} API keys")
        except Exception as e:
            logger.error(f"Error saving API keys: {e}")
            raise
    
    def create_key(self, role: str) -> APIKey:
        """Create a new API key."""
        if role not in ["user", "admin"]:
            raise ValueError("Role must be 'user' or 'admin'")
        
        # Generate a secure random key
        key = secrets.token_urlsafe(32)
        api_key = APIKey(key=key, role=role)
        
        # Store with key as ID
        self.keys[key] = api_key
        self._save_keys()
        
        logger.info(f"Created new {role} API key")
        return api_key
    
    def list_keys(self) -> List[APIKey]:
        """List all API keys."""
        return list(self.keys.values())
    
    def revoke_key(self, key: str) -> bool:
        """Revoke an API key."""
        if key not in self.keys:
            return False
        
        self.keys[key].revoked = True
        self._save_keys()
        logger.info(f"Revoked API key")
        return True
    
    def validate_key(self, key: str) -> Optional[str]:
        """Validate an API key and return its role if valid."""
        if key not in self.keys:
            return None
        
        api_key = self.keys[key]
        if api_key.revoked:
            return None
        
        return api_key.role
    
    def get_key_info(self, key: str) -> Optional[APIKey]:
        """Get information about an API key."""
        return self.keys.get(key)


def create_key_manager() -> KeyManager:
    """Create a key manager instance using the shared *data* directory."""
    # Get absolute *data* directory path (and ensure it exists)
    data_dir = get_data_dir()

    return KeyManager(data_dir=str(data_dir))


def generate_jwt_for_key(api_key: str, role: str) -> str:
    """Generate a JWT token for an API key."""
    # Use the same import path as the rest of the backend to avoid loading
    # the SQLModel metadata twice ("backend.app..." vs "app...").
    # Importing via the wrong namespace causes the *Organization* table to be
    # registered twice, triggering the "Table already defined" error when the
    # CLI command `manage-keys create` is executed.
    from app.auth.jwt import create_access_token
    
    payload = {
        "sub": f"{role}_user",
        "role": role
    }
    
    return create_access_token(payload) 