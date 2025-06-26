from typing import Optional

try:
    from email_spell_checker import EmailSpellChecker

    SPELL_CHECKER_AVAILABLE = True
except ImportError:
    SPELL_CHECKER_AVAILABLE = False
    EmailSpellChecker = None

from loguru import logger


def suggest_domain(domain: str) -> Optional[str]:
    """
    Suggest a corrected domain name using email-spell-checker.

    Args:
        domain: The domain to check for typos

    Returns:
        Corrected domain if a suggestion is found, None otherwise
    """
    if not SPELL_CHECKER_AVAILABLE:
        # During unit-tests the class may be patched in at runtime – check again.
        if EmailSpellChecker is None:
            logger.warning("email-spell-checker package not available, typo suggestions disabled")
            return None
        # If we get here, EmailSpellChecker was injected (e.g. via unittest.mock)

    try:
        spell_checker = EmailSpellChecker()
        suggestion = spell_checker.check_domain(domain)

        if suggestion and suggestion.lower() != domain.lower():
            logger.info(f"Domain typo suggestion: {domain} -> {suggestion}")
            return suggestion

        return None
    except Exception as e:
        logger.error(f"Error checking domain typo for {domain}: {e}")
        return None
