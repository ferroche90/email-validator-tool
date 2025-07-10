from datetime import datetime
from typing import Optional

import bcrypt
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from email_validator_tool.config import get_settings


class Organization(SQLModel, table=True):
    """Organization model for multi-tenancy"""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, index=True)
    slug: str = Field(max_length=100, unique=True, index=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    users: list["User"] = Relationship(back_populates="organization")


class User(SQLModel, table=True):
    """User model with organization relationship"""

    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True, index=True)
    hashed_password: str = Field(max_length=255)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    role: str = Field(default="user", max_length=50)  # user, admin, super_admin
    organization_id: Optional[int] = Field(default=None, foreign_key="organization.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    organization: Optional[Organization] = Relationship(back_populates="users")

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash a password using bcrypt with configurable work factor"""
        settings = get_settings()
        salt = bcrypt.gensalt(rounds=settings.BCRYPT_WORK_FACTOR)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def verify_password(self, password: str) -> bool:
        """Verify a password against the hashed password"""
        return bcrypt.checkpw(password.encode("utf-8"), self.hashed_password.encode("utf-8"))

    @property
    def full_name(self) -> str:
        """Get the user's full name"""
        return f"{self.first_name} {self.last_name}"


# Pydantic models for API requests/responses
class UserCreate(SQLModel):
    """Model for user creation"""

    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    organization_slug: Optional[str] = Field(default=None, max_length=100)

    def __init__(self, **data):
        super().__init__(**data)
        # Validate password length using configurable minimum
        settings = get_settings()
        if len(self.password) < settings.MINIMUM_PASSWORD_LENGTH:
            raise ValueError(f"Password must be at least {settings.MINIMUM_PASSWORD_LENGTH} characters long")


class UserResponse(SQLModel):
    """Model for user responses (excludes sensitive data)"""

    id: int
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool
    is_verified: bool
    role: str
    organization_id: Optional[int]
    created_at: datetime

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class OrganizationCreate(SQLModel):
    """Model for organization creation"""

    name: str = Field(max_length=255)
    slug: str = Field(max_length=100)


class OrganizationResponse(SQLModel):
    """Model for organization responses"""

    id: int
    name: str
    slug: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
