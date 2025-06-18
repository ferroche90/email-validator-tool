import pytest
from email_validator_tool.validators.catch_all import CatchAllValidator
from email_validator_tool.core.models import ValidationStatus

@pytest.mark.asyncio
async def test_catch_all_disabled_returns_valid():
    validator = CatchAllValidator()
    validator.settings.ENABLE_CATCH_ALL = False
    result = await validator.validate("user@example.com")
    assert result.status == ValidationStatus.VALID
