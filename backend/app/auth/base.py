import os
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from loguru import logger
from sqlmodel import Session, select

from email_validator_tool.config import get_settings
from email_validator_tool.key_manager import create_key_manager
from .jwt import verify_token
from ..database.database import get_session
from ..database.models import User, Organization

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)
    
    user_id: Optional[int] = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = session.exec(select(User).where(User.id == user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_current_user_with_key_manager(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Get current user from JWT token (fallback to API key for backward compatibility)"""
    token = credentials.credentials
    payload = verify_token(token)
    
    # Check if this is a database user token
    if "user_id" in payload:
        # This is a database user, we need the session
        # For now, return the payload with user info
        return {
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "role": payload.get("role"),
            "organization_id": payload.get("organization_id"),
            "is_database_user": True
        }
    
    # Fallback to API key authentication (legacy)
    key_manager = create_key_manager()
    role = key_manager.validate_key(token)
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "role": role,
        "is_database_user": False
    }


def require_role(required_role: str):
    """Dependency to require a specific role"""
    def role_checker(user: dict = Depends(get_current_user_with_key_manager)) -> dict:
        if user.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )
        return user
    return role_checker


def require_role_hybrid(required_role: str):
    """Dependency to require a specific role (works with both database users and API keys)"""
    def role_checker(user: dict = Depends(get_current_user_with_key_manager)) -> dict:
        if user.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )
        return user
    return role_checker


def get_current_user_with_org(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> tuple[User, Optional[Organization]]:
    """Get current user with their organization"""
    if user.organization_id is None:
        return user, None
    
    organization = session.exec(
        select(Organization).where(Organization.id == user.organization_id)
    ).first()
    
    return user, organization 