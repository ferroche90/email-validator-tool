"""
Role account validator.
"""

from loguru import logger
from email_validator_tool.core.models import ValidationResult, ValidationStatus

def is_role_account(email: str) -> bool:
    """Check if an email address is a role account."""
    common_roles = {
        'admin', 'administrator', 'webmaster', 'hostmaster', 'postmaster',
        'info', 'support', 'sales', 'contact', 'help', 'helpdesk',
        'noreply', 'no-reply', 'no_reply', 'donotreply', 'do-not-reply',
        'mail', 'mailer-daemon', 'abuse', 'security', 'marketing',
        'feedback', 'service', 'services', 'team', 'office', 'staff',
        'jobs', 'careers', 'recruitment', 'hr', 'human.resources',
        'billing', 'accounts', 'accounting', 'finance', 'legal',
        'privacy', 'press', 'media', 'marketing', 'advertising',
        'news', 'newsletter', 'subscribe', 'unsubscribe', 'welcome',
        'hello', 'hi', 'test', 'demo', 'example', 'sample'
    }
    
    local_part = email.split('@')[0].lower()
    return local_part in common_roles

class RoleAccountValidator:
    """Validator for role-based email accounts"""
    
    def __init__(self):
        """Initialize the validator"""
        self.role_accounts = {
            'admin', 'administrator', 'webmaster', 'hostmaster', 'postmaster',
            'info', 'support', 'help', 'contact', 'sales', 'marketing',
            'noreply', 'no-reply', 'donotreply', 'do-not-reply',
            'abuse', 'security', 'spam', 'feedback', 'mailer-daemon'
        }
    
    async def validate(self, email: str) -> ValidationResult:
        """
        Check if the email is a role-based account.
        
        Args:
            email: Email address to validate
            
        Returns:
            ValidationResult with the validation outcome
        """
        try:
            local_part = email.split('@')[0].lower()
            logger.debug(f"Checking if {local_part} is a role account")
            
            if local_part in self.role_accounts:
                logger.warning(f"Email {email} is a role account")
                return ValidationResult(
                    email=email,
                    status=ValidationStatus.ROLE_ACCOUNT,
                    details=f"Local part '{local_part}' is a role account"
                )
            
            logger.info(f"Email {email} is not a role account")
            return ValidationResult(
                email=email,
                status=ValidationStatus.VALID
            )
            
        except Exception as e:
            logger.error(f"Error validating role account status for {email}: {str(e)}")
            return ValidationResult(
                email=email,
                status=ValidationStatus.UNKNOWN_ERROR,
                details=str(e)
            )
