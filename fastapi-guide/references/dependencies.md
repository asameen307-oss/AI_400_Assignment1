# Dependency Injection

## Basic Dependency

```python
from typing import Annotated
from fastapi import Depends, FastAPI

app = FastAPI()

async def common_parameters(q: str = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
async def read_items(commons: Annotated[dict, Depends(common_parameters)]):
    return commons

@app.get("/users/")
async def read_users(commons: Annotated[dict, Depends(common_parameters)]):
    return commons
```

## Type Alias for Dependencies

```python
from typing import Annotated
from fastapi import Depends

CommonsDep = Annotated[dict, Depends(common_parameters)]

@app.get("/items/")
async def read_items(commons: CommonsDep):
    return commons
```

## Class as Dependency

```python
class CommonQueryParams:
    def __init__(self, q: str = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit

@app.get("/items/")
async def read_items(commons: Annotated[CommonQueryParams, Depends()]):
    # Shortcut: Depends() with no argument uses the type hint
    return {"q": commons.q, "skip": commons.skip}
```

## Nested Dependencies

```python
def query_extractor(q: str = None):
    return q

def query_or_cookie_extractor(
    q: Annotated[str, Depends(query_extractor)],
    last_query: str = Cookie(default=None)
):
    if not q:
        return last_query
    return q

@app.get("/items/")
async def read_query(
    query_or_default: Annotated[str, Depends(query_or_cookie_extractor)]
):
    return {"q_or_cookie": query_or_default}
```

## Dependencies with Yield (Cleanup)

```python
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/items/")
async def read_items(db: Annotated[Session, Depends(get_db)]):
    return db.query(Item).all()
```

## Path Operation Dependencies

```python
async def verify_token(x_token: str = Header(...)):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")

async def verify_key(x_key: str = Header(...)):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")

@app.get("/items/", dependencies=[Depends(verify_token), Depends(verify_key)])
async def read_items():
    return [{"item": "Foo"}]
```

## Router-Level Dependencies

```python
router = APIRouter(
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(verify_token)]
)

# All routes in this router require verify_token
@router.get("/")
async def read_items():
    return [{"item": "Foo"}]
```

## Global Dependencies

```python
app = FastAPI(dependencies=[Depends(verify_token)])

# All routes in the app require verify_token
```

## Dependency Caching

```python
# Dependencies are cached per-request by default
# Same dependency called multiple times = same result

async def get_value():
    print("Getting value")  # Only prints once per request
    return "value"

@app.get("/items/")
async def read_items(
    value1: Annotated[str, Depends(get_value)],
    value2: Annotated[str, Depends(get_value)]  # Uses cached value
):
    return {"value1": value1, "value2": value2}

# To disable caching:
@app.get("/items/")
async def read_items(
    value1: Annotated[str, Depends(get_value, use_cache=False)]
):
    return {"value1": value1}
```

## Dependency with Return Type

```python
from typing import Annotated
from fastapi import Depends

async def get_current_user(token: str = Header(...)) -> User:
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]

@app.get("/users/me")
async def read_users_me(current_user: CurrentUser):
    return current_user
```

## Sub-Dependencies Pattern

```python
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Validate token and return user
    pass

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not admin")
    return current_user

@app.get("/admin/")
async def admin_endpoint(admin: User = Depends(get_current_admin_user)):
    return {"admin": admin.username}
```
