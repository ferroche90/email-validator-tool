"""
Role account validator.
"""

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
    """Validator for role accounts."""
    
    def __init__(self):
        self.name = "role_account"
    
    async def validate(self, email: str, result) -> bool:
        """Validate if an email is not a role account."""
        if is_role_account(email):
            result.add_validation_result(
                self.name,
                False,
                "Email is a role account"
            )
            return False
        
        result.add_validation_result(
            self.name,
            True,
            None
        )
        return True
