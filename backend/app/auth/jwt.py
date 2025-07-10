"""
JWT authentication utilities with enhanced security features.
"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

import jwt
from email_validator_tool.config import get_settings
from fastapi import HTTPException, status
from jwt import PyJWTError
from loguru import logger


def create_access_token(payload: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with enhanced security features.

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

    # Add standard JWT claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": secrets.token_urlsafe(16),  # JWT ID for token uniqueness
        "aud": "email-validator-api",  # Audience claim
        "iss": "email-validator-service",  # Issuer claim
        "type": "access"  # Token type
    })

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    logger.debug(f"Created JWT access token for user with role: {payload.get('role', 'unknown')}")
    return encoded_jwt


def create_refresh_token(payload: Dict) -> str:
    """
    Create a JWT refresh token.

    Args:
        payload: Data to encode in the token

    Returns:
        Encoded JWT refresh token string
    """
    settings = get_settings()

    to_encode = payload.copy()

    # Refresh tokens have longer expiration
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    # Add standard JWT claims for refresh token
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": secrets.token_urlsafe(16),  # JWT ID for token uniqueness
        "aud": "email-validator-api",  # Audience claim
        "iss": "email-validator-service",  # Issuer claim
        "type": "refresh"  # Token type
    })

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    logger.debug(f"Created JWT refresh token for user with role: {payload.get('role', 'unknown')}")
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> dict:
    """
    Verify and decode a JWT token with enhanced validation.
    Supports both new tokens (with audience/issuer) and legacy tokens.

    Args:
        token: JWT token string
        token_type: Expected token type ("access" or "refresh")

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid, expired, or malformed
    """
    settings = get_settings()

    # Try to decode with new claims first (for new tokens)
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            audience="email-validator-api",
            issuer="email-validator-service",
        )

        # Validate token type if present
        if payload.get("type") and payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {token_type}",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.debug(f"Successfully verified JWT {token_type} token (new format) for role: {payload.get('role', 'unknown')}")
        return payload

    except (jwt.InvalidAudienceError, jwt.InvalidIssuerError):
        # Try legacy format (without audience/issuer validation)
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            
            logger.debug(f"Successfully verified JWT {token_type} token (legacy format) for role: {payload.get('role', 'unknown')}")
            return payload
            
        except PyJWTError as e:
            logger.warning(f"JWT token validation failed (legacy format): {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except PyJWTError as e:
        logger.warning(f"JWT token validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_access_token(token: str) -> dict:
    """Verify and decode a JWT access token."""
    return verify_token(token, "access")


def verify_refresh_token(token: str) -> dict:
    """Verify and decode a JWT refresh token."""
    return verify_token(token, "refresh")


def decode_token(token: str) -> Dict:
    """
    Decode and validate a JWT token (legacy function for backward compatibility).

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        PyJWTError: If token is invalid, expired, or malformed
    """
    settings = get_settings()

    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM],
            audience="email-validator-api",
            issuer="email-validator-service"
        )

        # Check if token has expired
        exp = payload.get("exp")
        if exp is None:
            raise PyJWTError("Token missing expiration")

        if datetime.now(timezone.utc) > datetime.fromtimestamp(exp, tz=timezone.utc):
            raise PyJWTError("Token has expired")

        logger.debug(f"Successfully decoded JWT token for role: {payload.get('role', 'unknown')}")
        return payload

    except PyJWTError as e:
        logger.warning(f"JWT token validation failed: {str(e)}")
        raise


def create_token_pair(payload: Dict) -> Dict[str, str]:
    """
    Create both access and refresh tokens.

    Args:
        payload: Data to encode in the tokens

    Returns:
        Dictionary containing access_token and refresh_token
    """
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
