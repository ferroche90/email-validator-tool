"""
Email validation modules.
"""

from . import bounce_list, catch_all, disposable, dns_mx, role_account, smtp, syntax
from . import spam_trap
from . import abuse_list, suppression
from . import typo_suggestion
from . import provider_type

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
