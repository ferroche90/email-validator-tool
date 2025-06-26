import asyncio
import time
from typing import Dict

from email_validator_tool.config import get_settings

# Keep track of last contact time per domain across validators
_last_contact: Dict[str, float] = {}

async def enforce_domain_delay(domain: str) -> None:
    """Ensure we wait PER_DOMAIN_DELAY_SECONDS between contacts to the same domain."""
    settings = get_settings()
    now = time.time()

    last = _last_contact.get(domain)
    if last is not None:
        elapsed = now - last
        delay = settings.PER_DOMAIN_DELAY_SECONDS - elapsed
        if delay > 0:
            await asyncio.sleep(delay)

    # record contact time
    _last_contact[domain] = time.time() 