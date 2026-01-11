---
name: fastapi-guide
description: |
  Hybrid Guide+Builder for FastAPI applications from hello world to production APIs.
  This skill should be used when users want to build FastAPI projects, create REST APIs,
  implement authentication, connect databases, or deploy Python web applications.
  Covers routing, Pydantic models, dependency injection, security, SQLModel, testing, and deployment.
---

# FastAPI Guide + Builder

Build FastAPI applications from beginner to production-grade APIs.

## Before Implementation

| Source | Gather |
|--------|--------|
| **Codebase** | Existing project structure, models, routers, dependencies |
| **Conversation** | User's specific requirements, API design, data models |
| **Skill References** | Patterns from `references/` (see table below) |
| **User Guidelines** | Project conventions, naming standards, auth requirements |

## Quick Reference

| Topic | Reference File |
|-------|----------------|
| Project setup, installation | `references/getting-started.md` |
| Path operations, routing | `references/routing.md` |
| Pydantic models, validation | `references/models.md` |
| Dependency injection | `references/dependencies.md` |
| Authentication, OAuth2, JWT | `references/security.md` |
| SQLModel database integration | `references/database.md` |
| Background tasks | `references/background-tasks.md` |
| Testing with pytest | `references/testing.md` |
| Deployment (Docker, Cloud) | `references/deployment.md` |
| WebSockets, streaming | `references/realtime.md` |
| Settings, configuration | `references/settings.md` |

---

## Workflow: Building FastAPI Projects

### Phase 1: Project Setup

```
1. Create project structure (see references/getting-started.md)
2. Install dependencies: pip install "fastapi[standard]"
3. Create main.py with FastAPI() instance
4. Run development server: fastapi dev main.py
```

**Minimal Hello World:**
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

### Phase 2: Define Data Models

```
1. Create Pydantic models for request/response validation
2. Use type hints for automatic validation
3. Define optional fields with default values
```

**Pattern:**
```python
from pydantic import BaseModel
from typing import Optional

class ItemCreate(BaseModel):
    name: str
    price: float
    description: Optional[str] = None

class ItemResponse(ItemCreate):
    id: int
```

### Phase 3: Create Path Operations

```
1. Define route handlers with decorators (@app.get, @app.post, etc.)
2. Use path parameters for resource identification
3. Use query parameters for filtering/pagination
4. Declare request body with Pydantic models
```

**Order matters:** Define specific paths before generic ones:
```python
@app.get("/users/me")      # First: specific
async def read_user_me(): ...

@app.get("/users/{user_id}")  # Second: generic
async def read_user(user_id: str): ...
```

### Phase 4: Organize with Routers

```
1. Create APIRouter instances for each domain
2. Apply prefix, tags, and shared dependencies
3. Include routers in main app
```

**Pattern:**
```python
# routers/items.py
from fastapi import APIRouter

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/")
async def list_items(): ...

# main.py
from routers import items
app.include_router(items.router)
```

### Phase 5: Add Database (SQLModel)

```
1. Define SQLModel models (table=True)
2. Create engine and session dependency
3. Use session in path operations
```

See `references/database.md` for complete patterns.

### Phase 6: Implement Security

```
1. Choose auth strategy (OAuth2 + JWT recommended)
2. Create token endpoint
3. Create dependency for current user
4. Protect routes with Depends()
```

See `references/security.md` for OAuth2 + JWT implementation.

### Phase 7: Testing

```
1. Use TestClient for synchronous tests
2. Write test functions (def, not async def)
3. Assert status codes and response bodies
```

**Pattern:**
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
```

### Phase 8: Production Deployment

```
1. Create Dockerfile (see references/deployment.md)
2. Configure environment variables
3. Set up reverse proxy if needed
4. Use multiple workers for production
```

---

## Key Decisions

| Decision | Recommendation |
|----------|----------------|
| Sync vs Async | Use `async def` for I/O-bound operations, `def` for CPU-bound |
| ORM | SQLModel (combines SQLAlchemy + Pydantic) |
| Auth | OAuth2 + JWT for stateless authentication |
| Validation | Pydantic models for all request/response |
| Config | pydantic-settings with .env files |
| Testing | pytest + TestClient |
| Deployment | Docker with fastapi run --workers |

## Anti-Patterns to Avoid

| Anti-Pattern | Correct Approach |
|--------------|------------------|
| Generic path before specific | Put `/users/me` before `/users/{id}` |
| Blocking sync code in async | Use `def` or run in thread pool |
| Hardcoded secrets | Use pydantic-settings + environment variables |
| No response_model | Always declare response_model for documentation |
| Testing with async def | Use regular `def` with TestClient |
| Single worker in production | Use `--workers 4` or more |

## Common Tasks

### Add CRUD Endpoint
1. Define Pydantic model (Create, Update, Response)
2. Create router with path operations
3. Implement database operations
4. Add to main app with include_router

### Add Authentication
1. Install python-jose, passlib
2. Create OAuth2PasswordBearer scheme
3. Implement password hashing
4. Create JWT token generation
5. Create get_current_user dependency

### Add Background Task
```python
from fastapi import BackgroundTasks

@app.post("/send-notification/")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email, email, "Welcome!")
    return {"message": "Notification scheduled"}
```

### Add WebSocket
```python
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")
```

### Configure CORS
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

### Custom Exception Handler
```python
from fastapi import HTTPException
from fastapi.responses import PlainTextResponse

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)
```

---

## Project Structure (Production)

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app instance
│   ├── config.py            # Settings with pydantic-settings
│   ├── dependencies.py      # Shared dependencies
│   ├── models/              # SQLModel/Pydantic models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── routers/             # API routers
│   │   ├── __init__.py
│   │   ├── users.py
│   │   └── items.py
│   ├── services/            # Business logic
│   │   └── auth.py
│   └── database.py          # Database connection
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── requirements.txt
├── Dockerfile
└── .env
```

## Lifespan Events

Use async context manager for startup/shutdown:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load resources
    print("Starting up...")
    yield
    # Shutdown: cleanup
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)
```

---

## Checklist: Production Ready

- [ ] All endpoints have response_model defined
- [ ] Authentication implemented for protected routes
- [ ] Input validation with Pydantic models
- [ ] Error handling with custom exception handlers
- [ ] CORS configured for frontend origins
- [ ] Environment variables for secrets (no hardcoded values)
- [ ] Tests written with TestClient
- [ ] Dockerfile created
- [ ] Multiple workers configured for deployment
- [ ] Logging configured
- [ ] Health check endpoint (`/health`)
