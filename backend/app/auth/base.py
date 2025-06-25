import os
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from loguru import logger

from email_validator_tool.config import get_settings
from email_validator_tool.key_manager import create_key_manager
from .jwt import decode_token

security = HTTPBearer()


def get_current_user_with_key_manager(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Authentication that supports API keys from key manager and JWT tokens.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Check if it's an API key from the key manager
    try:
        key_manager = create_key_manager()
        role = key_manager.validate_key(token)
        if role:
            logger.debug(f"API key authentication successful for role: {role}")
            return {"role": role, "sub": f"{role}_user", "api_key": True}
    except Exception as e:
        logger.warning(f"Error validating API key: {e}")
    
    # If not an API key, try JWT authentication
    try:
        payload = decode_token(token)
        logger.debug(f"JWT authentication successful for role: {payload.get('role')}")
        return payload
    except JWTError as e:
        # If JWT fails and it's not an API key, it's invalid
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_role_hybrid(required_role: str):
    """
    Dependency factory for role-based access control that supports JWT and API keys.
    
    Args:
        required_role: The role required to access the endpoint ('user' or 'admin')
    """
    def role_checker(user: dict = Depends(get_current_user_with_key_manager)):
        user_role = user.get("role")
        if user_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}, got: {user_role}"
            )
        return user
    return role_checker 