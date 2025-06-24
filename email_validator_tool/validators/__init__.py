"""
Email validation modules.
"""

from . import bounce_list, catch_all, disposable, dns_mx, role_account, smtp, syntax

__all__ = [
    "syntax",
    "dns_mx",
    "smtp",
    "catch_all",
    "bounce_list",
    "role_account",
    "disposable",
]
