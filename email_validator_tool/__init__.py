"""
Email Validator Tool - A comprehensive email validation package.
"""

__version__ = "0.1.0"

from .core.loader import EmailLoader
from .core.pipeline import ValidationPipeline
from .core.results import ValidationResult
from .validators import (
    bounce_list,
    catch_all,
    disposable,
    dns_mx,
    role_account,
    smtp,
    syntax,
)

__all__ = [
    "ValidationPipeline",
    "EmailLoader",
    "ValidationResult",
    "syntax",
    "dns_mx",
    "smtp",
    "catch_all",
    "bounce_list",
    "role_account",
    "disposable",
]
