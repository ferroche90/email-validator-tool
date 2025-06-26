from typing import Set

from email_validator_tool.core.models import ValidationResult, ValidationStatus
from email_validator_tool.utils.paths import get_data_dir
from loguru import logger

# Default free provider file location (relative to project root)
_FREE_PROVIDERS_FILE = get_data_dir() / "free_providers.txt"


def _load_free_providers_file() -> Set[str]:
    """Load free provider domains from the text file (one domain per line)."""
    providers: Set[str] = set()
    if not _FREE_PROVIDERS_FILE.exists():
        logger.warning(f"Free providers file '{_FREE_PROVIDERS_FILE}' not found – continuing with empty list.")
        return providers

    try:
        with _FREE_PROVIDERS_FILE.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip().lower()
                if not line or line.startswith("#"):
                    continue
                providers.add(line)
        logger.info(f"Loaded {len(providers)} free provider domains from '{_FREE_PROVIDERS_FILE}'.")
    except Exception as exc:
        logger.error(f"Error reading free providers file '{_FREE_PROVIDERS_FILE}': {exc}")
    return providers


class ProviderTypeValidator:
    """Validator that sets meta['free_provider'] based on free provider list."""

    def __init__(self):
        self.free_providers: Set[str] = _load_free_providers_file()

    def reload_free_providers(self) -> int:
        self.free_providers = _load_free_providers_file()
        return len(self.free_providers)

    async def validate(self, email: str) -> ValidationResult:
        """Set meta['free_provider'] in the result."""
        meta = {}
        try:
            if "@" not in email:
                return ValidationResult(email=email, status=ValidationStatus.VALID, meta=meta)
            domain = email.split("@", 1)[1].lower()
            is_free = domain in self.free_providers
            meta["free_provider"] = is_free
            return ValidationResult(email=email, status=ValidationStatus.VALID, meta=meta)
        except Exception as e:
            logger.error(f"Error in ProviderTypeValidator for {email}: {e}")
            return ValidationResult(email=email, status=ValidationStatus.VALID, meta=meta)
