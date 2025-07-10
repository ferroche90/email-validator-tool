"""
API routes for the email validator backend.
"""

from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from ..auth.base import get_current_user, get_current_user_from_refresh_token, require_role
from ..auth.jwt import create_access_token, create_refresh_token, create_token_pair
from ..database.database import get_session
from ..database.models import Organization, OrganizationCreate, OrganizationResponse, User, UserCreate, UserResponse
from email_validator_tool.key_manager import create_key_manager, APIKey

router = APIRouter()
security = HTTPBearer()


# Authentication routes
@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, session: Session = Depends(get_session)):
    """Register a new user"""
    # Check if user already exists
    existing_user = session.exec(
        session.query(User).where(User.email == user_data.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Create organization if specified
    organization = None
    if user_data.organization_slug:
        organization = session.exec(
            session.query(Organization).where(Organization.slug == user_data.organization_slug)
        ).first()
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization not found"
            )

    # Create user
    hashed_password = User.hash_password(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        organization_id=organization.id if organization else None
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return user


@router.post("/auth/login")
def login_user(email: str, password: str, session: Session = Depends(get_session)):
    """Login user and return JWT tokens"""
    user = session.exec(
        session.query(User).where(User.email == email)
    ).first()
    
    if not user or not user.verify_password(password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    # Create token payload
    payload = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
        "organization_id": user.organization_id
    }
    
    # Return both access and refresh tokens
    return create_token_pair(payload)


@router.post("/auth/refresh")
def refresh_access_token(user: User = Depends(get_current_user_from_refresh_token)):
    """Refresh access token using refresh token"""
    payload = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
        "organization_id": user.organization_id
    }
    
    return {
        "access_token": create_access_token(payload),
        "token_type": "bearer"
    }


# API Key Management routes
@router.post("/auth/api-keys", response_model=dict)
def create_api_key(role: str = "user", current_user: dict = Depends(require_role("admin"))):
    """Create a new API key (admin only)"""
    key_manager = create_key_manager()
    
    if role not in ["user", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be 'user' or 'admin'"
        )
    
    api_key = key_manager.create_key(role)
    
    return {
        "key": api_key.key,
        "role": api_key.role,
        "created_at": api_key.created_at.isoformat(),
        "message": "API key created successfully. Store it securely as it won't be shown again."
    }


@router.get("/auth/api-keys", response_model=List[dict])
def list_api_keys(current_user: dict = Depends(require_role("admin"))):
    """List all API keys (admin only)"""
    key_manager = create_key_manager()
    keys = key_manager.list_keys()
    
    return [
        {
            "key": key.key[:8] + "..." + key.key[-8:],  # Show only first/last 8 chars
            "role": key.role,
            "created_at": key.created_at.isoformat(),
            "revoked": key.revoked
        }
        for key in keys
    ]


@router.delete("/auth/api-keys/{key_id}")
def revoke_api_key(key_id: str, current_user: dict = Depends(require_role("admin"))):
    """Revoke an API key (admin only)"""
    key_manager = create_key_manager()
    
    # Find the key by partial match (since we only show partial keys in list)
    keys = key_manager.list_keys()
    target_key = None
    
    for key in keys:
        if key.key.startswith(key_id[:8]) and key.key.endswith(key_id[-8:]):
            target_key = key.key
            break
    
    if not target_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    success = key_manager.revoke_key(target_key)
    
    if success:
        return {"message": "API key revoked successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to revoke API key"
        )


@router.post("/auth/api-keys/{key_id}/rotate")
def rotate_api_key(key_id: str, current_user: dict = Depends(require_role("admin"))):
    """Rotate an API key (revoke old, create new)"""
    key_manager = create_key_manager()
    
    # Find the key by partial match
    keys = key_manager.list_keys()
    target_key = None
    target_role = None
    
    for key in keys:
        if key.key.startswith(key_id[:8]) and key.key.endswith(key_id[-8:]):
            target_key = key.key
            target_role = key.role
            break
    
    if not target_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Revoke old key
    key_manager.revoke_key(target_key)
    
    # Create new key with same role
    new_api_key = key_manager.create_key(target_role)
    
    return {
        "old_key": target_key[:8] + "..." + target_key[-8:],
        "new_key": new_api_key.key,
        "role": new_api_key.role,
        "created_at": new_api_key.created_at.isoformat(),
        "message": "API key rotated successfully. Store the new key securely."
    }


# User management routes
@router.get("/users/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.put("/users/me", response_model=UserResponse)
def update_current_user(
    first_name: str = None,
    last_name: str = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update current user information"""
    if first_name is not None:
        current_user.first_name = first_name
    if last_name is not None:
        current_user.last_name = last_name
    
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    
    return current_user


# Organization routes
@router.post("/organizations", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
    org_data: OrganizationCreate,
    current_user: dict = Depends(require_role("admin")),
    session: Session = Depends(get_session)
):
    """Create a new organization (admin only)"""
    # Check if organization already exists
    existing_org = session.exec(
        session.query(Organization).where(Organization.slug == org_data.slug)
    ).first()
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization with this slug already exists"
        )
    
    organization = Organization(
        name=org_data.name,
        slug=org_data.slug
    )
    
    session.add(organization)
    session.commit()
    session.refresh(organization)
    
    return organization


@router.get("/organizations", response_model=List[OrganizationResponse])
def list_organizations(
    current_user: dict = Depends(require_role("admin")),
    session: Session = Depends(get_session)
):
    """List all organizations (admin only)"""
    organizations = session.exec(session.query(Organization)).all()
    return organizations


# Health check
@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "email-validator-api"}


# Email validation routes (existing functionality)
@router.post("/validate/email")
def validate_single_email(email: str, current_user: dict = Depends(get_current_user_with_key_manager)):
    """Validate a single email address"""
    # This would integrate with your existing email validation logic
    # For now, return a placeholder response
    return {
        "email": email,
        "is_valid": True,
        "validation_details": {
            "syntax": True,
            "domain": True,
            "mx_record": True
        }
    }


@router.post("/validate/bulk")
def validate_bulk_emails(emails: List[str], current_user: dict = Depends(get_current_user_with_key_manager)):
    """Validate multiple email addresses"""
    # This would integrate with your existing bulk validation logic
    results = []
    for email in emails:
        results.append({
            "email": email,
            "is_valid": True,
            "validation_details": {
                "syntax": True,
                "domain": True,
                "mx_record": True
            }
        })
    
    return {
        "total_emails": len(emails),
        "valid_emails": len([r for r in results if r["is_valid"]]),
        "invalid_emails": len([r for r in results if not r["is_valid"]]),
        "results": results
    }
