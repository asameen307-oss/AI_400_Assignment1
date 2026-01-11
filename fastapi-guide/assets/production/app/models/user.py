"""User models."""
from typing import Optional

from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    """Base user model with shared attributes."""

    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    is_active: bool = True


class User(UserBase, table=True):
    """User database model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str


class UserCreate(UserBase):
    """Model for creating a user."""

    password: str


class UserUpdate(SQLModel):
    """Model for updating a user."""

    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserPublic(UserBase):
    """Model for public user response (no password)."""

    id: int
