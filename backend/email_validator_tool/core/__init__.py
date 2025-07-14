"""
Core components for email validation.
"""

from .domain_info import get_domain_info
from .loader import EmailLoader
from .pipeline import ValidationPipeline
from .results import ValidationResult

__all__ = ["ValidationPipeline", "EmailLoader", "ValidationResult", "get_domain_info"]
