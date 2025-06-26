"""
Core components for email validation.
"""

from .loader import EmailLoader
from .pipeline import ValidationPipeline
from .results import ValidationResult

__all__ = ["ValidationPipeline", "EmailLoader", "ValidationResult"]
