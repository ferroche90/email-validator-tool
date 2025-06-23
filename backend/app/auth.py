from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

security = HTTPBearer()

def get_current_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Get token from environment variable
    expected_token = os.getenv("API_TOKEN", "default_token_for_development")
    
    if not credentials or credentials.credentials != expected_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid auth credentials")
    return credentials.credentials 