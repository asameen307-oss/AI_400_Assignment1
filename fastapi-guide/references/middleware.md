# Middleware and Error Handling

## CORS Middleware

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

## HTTPS Redirect

```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
```

## Trusted Host

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com", "*.example.com"]
)
```

## GZip Compression

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

## Custom Middleware

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

app.add_middleware(TimingMiddleware)
```

## Middleware with @app.middleware

```python
@app.middleware("http")
async def add_custom_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Custom-Header"] = "Hello"
    return response
```

## Request Logging Middleware

```python
import logging

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Status: {response.status_code}")
    return response
```

---

# Error Handling

## HTTPException

```python
from fastapi import FastAPI, HTTPException, status

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found",
            headers={"X-Error": "Item error"}
        )
    return items[item_id]
```

## Custom Exception Handler

```python
from fastapi import Request
from fastapi.responses import JSONResponse

class ItemNotFoundException(Exception):
    def __init__(self, item_id: str):
        self.item_id = item_id

@app.exception_handler(ItemNotFoundException)
async def item_not_found_handler(request: Request, exc: ItemNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"message": f"Item {exc.item_id} not found"}
    )

@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id not in items:
        raise ItemNotFoundException(item_id)
    return items[item_id]
```

## Override Default HTTPException Handler

```python
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return PlainTextResponse(
        str(exc.detail),
        status_code=exc.status_code
    )
```

## Override Validation Exception Handler

```python
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    errors = []
    for error in exc.errors():
        errors.append(f"Field: {error['loc']}, Error: {error['msg']}")
    return PlainTextResponse(
        "Validation errors:\n" + "\n".join(errors),
        status_code=422
    )
```

## Global Exception Handler

```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"}
    )
```

## FastAPI vs Starlette HTTPException

From official docs:
> FastAPI's HTTPException inherits from Starlette's HTTPException.
> The key difference is that FastAPI's HTTPException accepts any
> JSON-serializable data for the detail field, while Starlette's
> only accepts strings.

```python
# FastAPI - accepts dict
raise HTTPException(
    status_code=400,
    detail={"error": "Bad request", "field": "name"}
)

# Register handlers for Starlette's HTTPException to catch all
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
```

## Error Response Model

```python
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None

@app.get("/items/{item_id}", responses={404: {"model": ErrorResponse}})
async def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )
    return items[item_id]
```
