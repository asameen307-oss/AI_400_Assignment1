"""Item models."""
from typing import Optional

from sqlmodel import Field, SQLModel


class ItemBase(SQLModel):
    """Base item model with shared attributes."""

    name: str = Field(index=True)
    description: Optional[str] = None
    price: float = Field(gt=0)


class Item(ItemBase, table=True):
    """Item database model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")


class ItemCreate(ItemBase):
    """Model for creating an item."""

    pass


class ItemUpdate(SQLModel):
    """Model for updating an item."""

    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None


class ItemPublic(ItemBase):
    """Model for public item response."""

    id: int
    owner_id: Optional[int] = None
