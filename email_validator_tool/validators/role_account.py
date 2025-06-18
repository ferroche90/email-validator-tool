import re
from email_role_detector import is_role_account
from email_validator_tool.models import ValidationResult, ValidationStatus

# Comprehensive list of role account patterns
ROLE_PATTERNS = [
    # Administrative roles
    r'^admin$', r'^administrator$', r'^webmaster$', r'^hostmaster$', r'^postmaster$',
    r'^root$', r'^sysadmin$', r'^system$', r'^server$', r'^daemon$',
    
    # Support and help
    r'^support$', r'^help$', r'^helpdesk$', r'^assist$', r'^assistance$',
    r'^customer[-_]?service$', r'^customerservice$', r'^customer[-_]?support$',
    r'^customersupport$', r'^tech[-_]?support$', r'^techsupport$',
    
    # Information and contact
    r'^info$', r'^information$', r'^contact$', r'^contactus$', r'^contact[-_]?us$',
    r'^hello$', r'^hi$', r'^greetings$', r'^welcome$', r'^get[-_]?started$',
    
    # Sales and marketing
    r'^sales$', r'^marketing$', r'^advertise$', r'^advertising$', r'^promo$',
    r'^promotion$', r'^business$', r'^commercial$', r'^partnership$',
    
    # Communication
    r'^news$', r'^newsletter$', r'^press$', r'^media$', r'^pr$', r'^public[-_]?relations$',
    r'^subscribe$', r'^subscription$', r'^unsubscribe$', r'^opt[-_]?out$',
    
    # No-reply and automated
    r'^noreply$', r'^no[-_]?reply$', r'^no[-_]?response$', r'^donotreply$',
    r'^do[-_]?not[-_]?reply$', r'^automated$', r'^auto$', r'^automatic$',
    
    # Security and abuse
    r'^security$', r'^abuse$', r'^spam$', r'^fraud$', r'^phishing$',
    r'^malware$', r'^virus$', r'^antivirus$', r'^antispam$',
    
    # Common prefixes
    r'^team[-_]?', r'^our[-_]?', r'^the[-_]?', r'^my[-_]?', r'^your[-_]?',
    
    # Common suffixes
    r'[-_]?team$', r'[-_]?support$', r'[-_]?help$', r'[-_]?info$', r'[-_]?contact$',
    r'[-_]?sales$', r'[-_]?marketing$', r'[-_]?media$', r'[-_]?press$',
    
    # Generic roles
    r'^office$', r'^main$', r'^general$', r'^global$', r'^worldwide$',
    r'^international$', r'^corporate$', r'^company$', r'^enterprise$',
    
    # Common combinations
    r'^contact[-_]?us$', r'^get[-_]?in[-_]?touch$', r'^reach[-_]?out$',
    r'^send[-_]?message$', r'^drop[-_]?us[-_]?line$', r'^say[-_]?hello$'
]

async def check(email: str) -> ValidationResult:
    # First check using email-role-detector
    if is_role_account(email):
        return ValidationResult(
            email=email,
            status=ValidationStatus.ROLE_ACCOUNT,
            details="Detected as role account by email-role-detector"
        )
    
    # Then check using our regex patterns
    local_part = email.split('@')[0].lower()
    
    for pattern in ROLE_PATTERNS:
        if re.match(pattern, local_part, re.IGNORECASE):
            return ValidationResult(
                email=email,
                status=ValidationStatus.ROLE_ACCOUNT,
                details=f"Local part '{local_part}' matches role account pattern '{pattern}'"
            )
    
    return ValidationResult(
        email=email,
        status=ValidationStatus.VALID
    )
