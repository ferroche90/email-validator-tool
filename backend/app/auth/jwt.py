"""
JWT authentication utilities.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from jose import JWTError, jwt
from loguru import logger

from email_validator_tool.config import get_settings


def create_access_token(payload: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        payload: Data to encode in the token
        expires_delta: Optional expiration time override
        
    Returns:
        Encoded JWT token string
    """
    settings = get_settings()
    
    to_encode = payload.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    
    logger.debug(f"Created JWT token for user with role: {payload.get('role', 'unknown')}")
    return encoded_jwt


def decode_token(token: str) -> Dict:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        JWTError: If token is invalid, expired, or malformed
    """
    settings = get_settings()
    
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Check if token has expired
        exp = payload.get("exp")
        if exp is None:
            raise JWTError("Token missing expiration")
            
        if datetime.now(timezone.utc) > datetime.fromtimestamp(exp, tz=timezone.utc):
            raise JWTError("Token has expired")
            
        logger.debug(f"Successfully decoded JWT token for role: {payload.get('role', 'unknown')}")
        return payload
        
    except JWTError as e:
        logger.warning(f"JWT token validation failed: {str(e)}")
        raise 