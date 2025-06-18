import tempfile
from pathlib import Path
import pytest
from email_validator_tool.validators.bounce_list import BounceListValidator
from email_validator_tool.core.models import ValidationStatus

@pytest.mark.asyncio
async def test_bounce_list_detection():
    tmp = Path(tempfile.mkstemp()[1])
    validator = BounceListValidator(db_path=tmp)
    validator.add_email("bounced@example.com")
    result = await validator.validate("bounced@example.com")
    assert result.status == ValidationStatus.ON_BOUNCE_LIST
    tmp.unlink()
