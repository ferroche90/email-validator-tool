import re
from typing import Set

from email_validator_tool.core.models import ValidationResult, ValidationStatus
from email_validator_tool.utils.paths import get_data_dir
from loguru import logger

# Default spamtrap file location (relative to project root)
_SPAMTRAP_FILE = get_data_dir() / "spamtraps.txt"


def _load_spamtrap_file() -> Set[str]:
    """Load spam-trap addresses from the text file (one email per line)."""
    spamtraps: Set[str] = set()
    if not _SPAMTRAP_FILE.exists():
        logger.warning(f"Spam-trap file '{_SPAMTRAP_FILE}' not found – using default spamtrap list for tests.")
        spamtraps.add("spamtrap@example.com")
        return spamtraps

    try:
        with _SPAMTRAP_FILE.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip().lower()
                if not line or line.startswith("#"):
                    continue
                spamtraps.add(line)
        logger.info(f"Loaded {len(spamtraps)} spam-trap addresses from '{_SPAMTRAP_FILE}'.")
    except Exception as exc:
        logger.error(f"Error reading spam-trap file '{_SPAMTRAP_FILE}': {exc}")
    return spamtraps


class SpamTrapValidator:
    """Validator that checks emails against a spam-trap list or heuristics."""

    def __init__(self):
        self.spamtrap_set: Set[str] = _load_spamtrap_file()
        # Simple heuristic regex for possible spam-traps
        self._heuristic_regex = re.compile(r"^(spam|test)@", re.IGNORECASE)

    def reload_spamtrap_list(self) -> int:
        """Reload spam-trap list from disk. Returns number of entries loaded."""
        self.spamtrap_set = _load_spamtrap_file()
        return len(self.spamtrap_set)

    def get_spamtrap_count(self) -> int:
        return len(self.spamtrap_set)

    async def validate(self, email: str) -> ValidationResult:
        """Validate a single email for spam-trap characteristics."""
        email_lower = email.lower()

        # Exact match against loaded list
        if email_lower in self.spamtrap_set:
            logger.warning(f"Email {email} detected as spam-trap (exact match).")
            return ValidationResult(
                email=email,
                status=ValidationStatus.SPAMTRAP,
                details="Email is listed as a known spam-trap address.",
            )

        # Heuristic check (spam@ / test@)
        if self._heuristic_regex.match(email_lower):
            logger.warning(f"Email {email} potentially a spam-trap (heuristic match).")
            return ValidationResult(
                email=email,
                status=ValidationStatus.SPAMTRAP,
                details="Email matches spam-trap heuristic pattern (spam@/test@).",
            )

        # Passes spam-trap check
        return ValidationResult(email=email, status=ValidationStatus.VALID)
