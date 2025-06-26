"""
Email validation modules.
"""

from . import (
    abuse_list,
    bounce_list,
    catch_all,
    disposable,
    dns_mx,
    provider_type,
    role_account,
    smtp,
    spam_trap,
    suppression,
    syntax,
    typo_suggestion,
)

__all__ = [
    "syntax",
    "dns_mx",
    "smtp",
    "catch_all",
    "bounce_list",
    "role_account",
    "disposable",
    "spam_trap",
    "abuse_list",
    "suppression",
    "typo_suggestion",
    "provider_type",
]
