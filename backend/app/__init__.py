"""
Email Validator Backend Application.

This module provides the main FastAPI application and related components.
"""

from .main import app
from .auth import get_current_token
from .core_settings import BackendSettings
from .api import router as api_router

__all__ = ["app", "get_current_token", "BackendSettings", "api_router"]
