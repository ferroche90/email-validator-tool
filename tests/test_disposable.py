import pytest
from email_validator_tool.validators.disposable import DisposableValidator
from email_validator_tool.core.models import ValidationStatus

@pytest.mark.asyncio
async def test_disposable_detected():
    validator = DisposableValidator()
    result = await validator.validate("user@mailinator.com")
    assert result.status == ValidationStatus.DISPOSABLE

@pytest.mark.asyncio
async def test_non_disposable():
    validator = DisposableValidator()
    result = await validator.validate("user@example.com")
    assert result.status == ValidationStatus.VALID
