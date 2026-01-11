# Routing and Path Operations

## HTTP Methods

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/")
async def read_items():
    return [{"item": "Foo"}]

@app.post("/items/")
async def create_item(item: Item):
    return item

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}

@app.patch("/items/{item_id}")
async def partial_update(item_id: int, item: ItemUpdate):
    return {"item_id": item_id}

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    return {"deleted": item_id}
```

## Path Parameters

```python
@app.get("/items/{item_id}")
async def read_item(item_id: int):  # Automatic type conversion
    return {"item_id": item_id}

# Multiple path parameters
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(user_id: int, item_id: str):
    return {"user_id": user_id, "item_id": item_id}
```

## Path Order (Critical)

**Specific paths must be declared before generic paths:**

```python
# CORRECT ORDER
@app.get("/users/me")           # 1. Specific first
async def read_user_me():
    return {"user_id": "the current user"}

@app.get("/users/{user_id}")    # 2. Generic second
async def read_user(user_id: str):
    return {"user_id": user_id}
```

## Query Parameters

```python
from typing import Optional

@app.get("/items/")
async def read_items(
    skip: int = 0,                      # Required with default
    limit: int = 10,                    # Required with default
    q: Optional[str] = None             # Optional
):
    return {"skip": skip, "limit": limit, "q": q}

# URL: /items/?skip=0&limit=10&q=search
```

## Query Parameter Validation

```python
from fastapi import Query

@app.get("/items/")
async def read_items(
    q: str = Query(
        default=None,
        min_length=3,
        max_length=50,
        pattern="^fixedquery$",
        title="Query string",
        description="Query string for search",
        deprecated=False
    )
):
    return {"q": q}

# Required query parameter
@app.get("/items/")
async def read_items(q: str = Query(...)):  # ... means required
    return {"q": q}
```

## Path Parameter Validation

```python
from fastapi import Path

@app.get("/items/{item_id}")
async def read_item(
    item_id: int = Path(
        ...,
        title="Item ID",
        description="The ID of the item",
        ge=1,           # Greater than or equal
        le=1000         # Less than or equal
    )
):
    return {"item_id": item_id}
```

## Request Body

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    description: Optional[str] = None

@app.post("/items/")
async def create_item(item: Item):
    return item

# Multiple body parameters
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, user: User):
    return {"item_id": item_id, "item": item, "user": user}
```

## Header Parameters

```python
from fastapi import Header

@app.get("/items/")
async def read_items(
    user_agent: str = Header(default=None),
    x_token: str = Header(...)  # Custom header (auto-converts x_token to X-Token)
):
    return {"User-Agent": user_agent, "X-Token": x_token}
```

## Cookie Parameters

```python
from fastapi import Cookie

@app.get("/items/")
async def read_items(session_id: str = Cookie(default=None)):
    return {"session_id": session_id}
```

## Form Data

```python
from fastapi import Form

@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}
```

## File Upload

```python
from fastapi import File, UploadFile

# Simple file
@app.post("/files/")
async def create_file(file: bytes = File(...)):
    return {"file_size": len(file)}

# UploadFile (recommended for large files)
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    contents = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents)
    }

# Multiple files
@app.post("/files/")
async def create_files(files: list[UploadFile]):
    return {"filenames": [f.filename for f in files]}
```

## APIRouter

```python
# routers/items.py
from fastapi import APIRouter, Depends

router = APIRouter(
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}}
)

@router.get("/")
async def read_items():
    return [{"name": "Item Foo"}]

@router.get("/{item_id}")
async def read_item(item_id: str):
    return {"name": "Item Foo", "item_id": item_id}

# main.py
from fastapi import FastAPI
from routers import items

app = FastAPI()
app.include_router(items.router)

# Include with overrides
app.include_router(
    items.router,
    prefix="/api/v1",
    tags=["v1-items"],
    dependencies=[Depends(get_api_key)]
)
```

## Response Model

```python
from pydantic import BaseModel

class ItemOut(BaseModel):
    name: str
    price: float
    # Note: password field excluded

@app.post("/items/", response_model=ItemOut)
async def create_item(item: ItemIn):
    return item  # password automatically filtered out

# Exclude unset values
@app.get("/items/{item_id}", response_model=Item, response_model_exclude_unset=True)
async def read_item(item_id: str):
    return items[item_id]
```

## Status Codes

```python
from fastapi import status

@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    return item

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: str):
    return None
```
