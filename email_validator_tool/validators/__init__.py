"""
Email validation modules.
"""

from . import syntax
from . import dns_mx
from . import smtp
from . import catch_all
from . import bounce_list
from . import role_account
from . import disposable

__all__ = [
    'syntax',
    'dns_mx',
    'smtp',
    'catch_all',
    'bounce_list',
    'role_account',
    'disposable'
]
