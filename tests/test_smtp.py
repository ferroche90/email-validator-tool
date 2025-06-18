import pytest
from email_validator_tool.validators.smtp import SMTPValidator
from email_validator_tool.core.models import ValidationStatus

@pytest.mark.asyncio
async def test_invalid_domain():
    validator = SMTPValidator()
    result = await validator.validate("user@invalid-domain.test")
    assert result.status in {ValidationStatus.INVALID_DOMAIN, ValidationStatus.UNKNOWN_ERROR}
