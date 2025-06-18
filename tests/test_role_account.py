import pytest
from email_validator_tool.validators.role_account import RoleAccountValidator
from email_validator_tool.core.models import ValidationStatus

@pytest.mark.asyncio
async def test_role_account_detected():
    validator = RoleAccountValidator()
    result = await validator.validate("admin@example.com")
    assert result.status == ValidationStatus.ROLE_ACCOUNT

@pytest.mark.asyncio
async def test_regular_account():
    validator = RoleAccountValidator()
    result = await validator.validate("user@example.com")
    assert result.status == ValidationStatus.VALID
