"""
JWT authentication utilities.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

import jwt
from email_validator_tool.config import get_settings
from fastapi import HTTPException, status
from loguru import logger

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


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

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    logger.debug(f"Created JWT token for user with role: {payload.get('role', 'unknown')}")
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify and decode a JWT token using the runtime settings."""

    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


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
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

        # Check if token has expired
        exp = payload.get("exp")
        if exp is None:
            raise jwt.JWTError("Token missing expiration")

        if datetime.now(timezone.utc) > datetime.fromtimestamp(exp, tz=timezone.utc):
            raise jwt.JWTError("Token has expired")

        logger.debug(f"Successfully decoded JWT token for role: {payload.get('role', 'unknown')}")
        return payload

    except jwt.JWTError as e:
        logger.warning(f"JWT token validation failed: {str(e)}")
        raise
