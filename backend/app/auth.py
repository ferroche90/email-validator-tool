from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def get_current_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Placeholder: Accept any token for now
    if not credentials:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid auth credentials")
    return credentials.credentials 