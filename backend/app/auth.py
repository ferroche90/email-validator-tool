import os

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from email_validator_tool.config import get_settings

security = HTTPBearer()


def get_current_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Get token from settings
    settings = get_settings()
    expected_token = settings.API_TOKEN

    if not credentials or credentials.credentials != expected_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid auth credentials")
    return credentials.credentials
