"""
Core components for email validation.
"""

from .pipeline import ValidationPipeline
from .loader import EmailLoader
from .results import ValidationResult

__all__ = [
    'ValidationPipeline',
    'EmailLoader',
    'ValidationResult'
]
