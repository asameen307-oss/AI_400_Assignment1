"""Item routes."""
from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select

from app.database import SessionDep
from app.models import Item, ItemCreate, ItemPublic, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemPublic, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, session: SessionDep):
    """Create a new item."""
    db_item = Item.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.get("/", response_model=list[ItemPublic])
def read_items(
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    """Get all items with pagination."""
    items = session.exec(select(Item).offset(offset).limit(limit)).all()
    return items


@router.get("/{item_id}", response_model=ItemPublic)
def read_item(item_id: int, session: SessionDep):
    """Get a specific item by ID."""
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.patch("/{item_id}", response_model=ItemPublic)
def update_item(item_id: int, item: ItemUpdate, session: SessionDep):
    """Update an item."""
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    item_data = item.model_dump(exclude_unset=True)
    db_item.sqlmodel_update(item_data)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.delete("/{item_id}")
def delete_item(item_id: int, session: SessionDep):
    """Delete an item."""
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    session.delete(item)
    session.commit()
    return {"ok": True}
