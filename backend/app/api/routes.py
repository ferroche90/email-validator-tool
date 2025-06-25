from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

from email_validator_tool.config import get_settings
from email_validator_tool.key_manager import create_key_manager
from email_validator_tool.validators.bounce_list import BounceListValidator
from email_validator_tool.validators.dns_mx import DNSMXValidator

from app.auth.base import get_current_user_with_key_manager, require_role_hybrid
from app.auth.jwt import create_access_token
from ..services.validator_adapter import EmailValidatorService

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

# Global validator instances for sharing across requests
_settings = get_settings()
_global_dns_validator = DNSMXValidator(
    cache_ttl_seconds=(_settings.DNS_CACHE_TTL_SECONDS if _settings.ENABLE_DNS_CACHE else 0)
)
_global_bounce_validator = BounceListValidator()


class ValidateRequest(BaseModel):
    emails: List[str]
    enable_smtp: bool = False
    enable_catch_all: bool = False


class TokenRequest(BaseModel):
    api_key: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


def get_validator_service() -> EmailValidatorService:
    """Dependency to inject EmailValidatorService with global validator instances"""
    return EmailValidatorService(dns_validator=_global_dns_validator, bounce_validator=_global_bounce_validator)


@router.post("/token", response_model=TokenResponse)
@limiter.limit("100/minute")
async def create_token(request: Request, token_request: TokenRequest):
    """
    Create a JWT access token using a pre-provisioned API key.
    Rate limited to 100 requests per minute per IP.
    """
    # Try to validate the API key using the key manager
    key_manager = create_key_manager()
    role = key_manager.validate_key(token_request.api_key)
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked API key"
        )
    
    # Create token payload
    payload = {
        "sub": f"{role}_user",
        "role": role
    }
    
    access_token = create_access_token(payload)
    
    return TokenResponse(
        access_token=access_token,
        role=role
    )


@router.post("/validate")
@limiter.limit("20/minute")
async def validate_emails(
    request: Request,
    body: ValidateRequest,
    validator_service: EmailValidatorService = Depends(get_validator_service),
    user: dict = Depends(get_current_user_with_key_manager),
):
    """
    Validate a list of email addresses.
    Rate limited to 20 requests per minute per IP.
    Uses shared validator instances for better performance.
    """
    try:
        results = await validator_service.validate_many(
            emails=body.emails,
            enable_smtp=body.enable_smtp,
            enable_catch_all=body.enable_catch_all,
        )
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")


@router.get("/cache-stats")
@limiter.limit("5/minute")
async def get_cache_stats(request: Request, user: dict = Depends(require_role_hybrid("admin"))):
    """
    Get DNS cache statistics.
    Admin access required. Rate limited to 5 requests per minute.
    """
    try:
        stats = _global_dns_validator.get_cache_stats()
        return {
            "cache_stats": stats,
            "cache_enabled": _settings.ENABLE_DNS_CACHE,
            "cache_ttl_seconds": _settings.DNS_CACHE_TTL_SECONDS,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cache stats: {str(e)}")


@router.post("/cache-clear")
@limiter.limit("5/minute")
async def clear_cache(request: Request, user: dict = Depends(require_role_hybrid("admin"))):
    """
    Clear DNS cache.
    Admin access required. Rate limited to 5 requests per minute.
    """
    try:
        cleared_count = _global_dns_validator.clear_cache()
        return {
            "cleared": cleared_count,
            "message": f"DNS cache cleared successfully. Removed {cleared_count} entries.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")


@router.get("/bounce-stats")
@limiter.limit("5/minute")
async def get_bounce_stats(request: Request, user: dict = Depends(require_role_hybrid("admin"))):
    """
    Get bounce list statistics.
    Admin access required. Rate limited to 5 requests per minute.
    """
    try:
        bounce_count = _global_bounce_validator.get_bounce_count()
        return {
            "bounce_count": bounce_count,
            "loaded_in_memory": True,
            "database_path": "bounce_list.db",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting bounce stats: {str(e)}")
