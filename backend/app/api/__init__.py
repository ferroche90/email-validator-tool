"""
Email Validator API module.

This module provides the FastAPI router and endpoints for email validation.
"""

from .routes import ValidateRequest, router

__all__ = ["router", "ValidateRequest"]
