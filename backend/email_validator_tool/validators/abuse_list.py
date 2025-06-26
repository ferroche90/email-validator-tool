from pathlib import Path
from typing import Set

from loguru import logger

from email_validator_tool.core.models import ValidationResult, ValidationStatus
from email_validator_tool.utils.paths import get_data_dir

# Default abuse list file location (relative to project root)
_ABUSE_FILE = get_data_dir() / "abuse_list.txt"


def _load_abuse_file() -> Set[str]:
    """Load abuse/complainer emails from the text file (one email per line)."""
    abuse_emails: Set[str] = set()
    if not _ABUSE_FILE.exists():
        logger.warning(f"Abuse list file '{_ABUSE_FILE}' not found – continuing with empty list.")
        return abuse_emails

    try:
        with _ABUSE_FILE.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip().lower()
                if not line or line.startswith("#"):
                    continue
                abuse_emails.add(line)
        logger.info(f"Loaded {len(abuse_emails)} abuse emails from '{_ABUSE_FILE}'.")
    except Exception as exc:
        logger.error(f"Error reading abuse list file '{_ABUSE_FILE}': {exc}")
    return abuse_emails


class AbuseListValidator:
    """Validator that checks emails against a public abuse/complainer list."""

    def __init__(self):
        self.abuse_set: Set[str] = _load_abuse_file()

    def reload_abuse_list(self) -> int:
        """Reload abuse list from disk. Returns number of entries loaded."""
        self.abuse_set = _load_abuse_file()
        return len(self.abuse_set)

    def get_abuse_count(self) -> int:
        return len(self.abuse_set)

    async def validate(self, email: str) -> ValidationResult:
        """Validate a single email against the abuse list."""
        email_lower = email.lower()

        # Exact match against loaded list
        if email_lower in self.abuse_set:
            logger.warning(f"Email {email} detected as abuse/complainer (exact match).")
            return ValidationResult(
                email=email,
                status=ValidationStatus.ABUSE,
                details="Email is on the public abuse/complainer list.",
            )

        # Passes abuse check
        return ValidationResult(email=email, status=ValidationStatus.VALID)
