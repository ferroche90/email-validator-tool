from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlmodel import Session, select

from email_validator_tool.config import get_settings
from email_validator_tool.key_manager import create_key_manager
from email_validator_tool.validators.bounce_list import BounceListValidator
from email_validator_tool.validators.dns_mx import DNSMXValidator
from email_validator_tool.validators.spam_trap import SpamTrapValidator
from email_validator_tool.validators.abuse_list import AbuseListValidator
from email_validator_tool.validators.suppression import SuppressionValidator

from app.auth.base import get_current_user_with_key_manager, require_role_hybrid
from app.auth.jwt import create_access_token
from app.database.database import get_session
from app.database.models import User, Organization, UserCreate, UserResponse, OrganizationCreate
from app.metrics import increment_emails_validated, record_batch_size
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
_global_spamtrap_validator = SpamTrapValidator()
_global_abuse_validator = AbuseListValidator()
_global_suppression_validator = SuppressionValidator()


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


class SignupRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    organization_name: str
    organization_slug: str


class SignupResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class SuppressionRequest(BaseModel):
    emails: List[str]


def get_validator_service() -> EmailValidatorService:
    """Dependency to inject EmailValidatorService with global validator instances"""
    return EmailValidatorService(
        dns_validator=_global_dns_validator,
        bounce_validator=_global_bounce_validator,
        spamtrap_validator=_global_spamtrap_validator,
        abuse_validator=_global_abuse_validator,
        suppression_validator=_global_suppression_validator,
    )


@router.post("/signup", response_model=SignupResponse)
@limiter.limit("10/minute")
async def signup(request: Request, signup_data: SignupRequest, session: Session = Depends(get_session)):
    """
    Create a new user account with organization.
    Rate limited to 10 requests per minute per IP.
    """
    # Check if user already exists
    existing_user = session.exec(select(User).where(User.email == signup_data.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Check if organization slug already exists
    existing_org = session.exec(select(Organization).where(Organization.slug == signup_data.organization_slug)).first()
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization with this slug already exists"
        )
    
    # Create organization
    organization = Organization(
        name=signup_data.organization_name,
        slug=signup_data.organization_slug
    )
    session.add(organization)
    session.commit()
    session.refresh(organization)
    
    # Create user
    user = User(
        email=signup_data.email,
        hashed_password=User.hash_password(signup_data.password),
        first_name=signup_data.first_name,
        last_name=signup_data.last_name,
        organization_id=organization.id,
        role="admin"  # First user in organization is admin
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Create JWT token
    payload = {
        "sub": user.email,
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
        "organization_id": user.organization_id
    }
    access_token = create_access_token(payload)
    
    return SignupResponse(
        access_token=access_token,
        user=UserResponse.from_orm(user)
    )


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
    
    # Create token payload (legacy API key tokens don't have organization_id)
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
        # Get organization ID for metrics
        organization_id = user.get("organization_id", "unknown")
        if organization_id == "unknown" and user.get("is_database_user"):
            # For database users, get organization from session
            session = next(get_session())
            user_obj = session.exec(select(User).where(User.id == user.get("user_id"))).first()
            organization_id = str(user_obj.organization_id) if user_obj and user_obj.organization_id else "unknown"
        
        # Record batch size
        record_batch_size(organization_id, len(body.emails))
        
        results = await validator_service.validate_many(
            emails=body.emails,
            enable_smtp=body.enable_smtp,
            enable_catch_all=body.enable_catch_all,
        )
        
        # Record metrics for each validation result
        for result in results:
            increment_emails_validated(result.status, organization_id)
        
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


@router.post("/admin/reload-spamtraps")
@limiter.limit("5/minute")
async def reload_spamtraps(request: Request, user: dict = Depends(require_role_hybrid("admin"))):
    """Reload the spam-trap list from disk. Admin access required."""
    try:
        count = _global_spamtrap_validator.reload_spamtrap_list()
        return {
            "reload_count": count,
            "message": f"Spam-trap list reloaded successfully. Loaded {count} entries.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reloading spamtraps: {str(e)}")


@router.post("/admin/suppressions")
@limiter.limit("5/minute")
async def add_suppressions(
    request: Request,
    body: SuppressionRequest,
    user: dict = Depends(require_role_hybrid("admin"))
):
    """Add emails to the suppression list. Admin access required."""
    try:
        # Convert to set and normalize emails
        email_set = {email.strip().lower() for email in body.emails if email.strip()}
        added_count = _global_suppression_validator.add_suppressions(email_set)
        return {
            "added_count": added_count,
            "total_suppressions": _global_suppression_validator.get_suppression_count(),
            "message": f"Added {added_count} new suppressions. Total: {_global_suppression_validator.get_suppression_count()}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding suppressions: {str(e)}")


@router.get("/admin/suppression-stats")
@limiter.limit("5/minute")
async def get_suppression_stats(request: Request, user: dict = Depends(require_role_hybrid("admin"))):
    """Get suppression list statistics. Admin access required."""
    try:
        suppression_count = _global_suppression_validator.get_suppression_count()
        return {
            "suppression_count": suppression_count,
            "loaded_in_memory": True,
            "database_path": "suppression_list.db",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting suppression stats: {str(e)}")


@router.get("/admin/abuse-stats")
@limiter.limit("5/minute")
async def get_abuse_stats(request: Request, user: dict = Depends(require_role_hybrid("admin"))):
    """Get abuse list statistics. Admin access required."""
    try:
        abuse_count = _global_abuse_validator.get_abuse_count()
        return {
            "abuse_count": abuse_count,
            "loaded_in_memory": True,
            "file_path": "data/abuse_list.txt",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting abuse stats: {str(e)}")
