# FastAPI Testing Reference

## Table of Contents
1. [TestClient Basics](#testclient-basics)
2. [Testing HTTP Methods](#testing-http-methods)
3. [Request Patterns](#request-patterns)
4. [Dependency Overrides](#dependency-overrides)
5. [Async Testing](#async-testing)
6. [Database Testing](#database-testing)
7. [Authentication Testing](#authentication-testing)
8. [WebSocket Testing](#websocket-testing)
9. [Background Tasks Testing](#background-tasks-testing)

---

## TestClient Basics

### Installation
```bash
pip install httpx pytest
```

### Basic Test
```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
```

### TestClient as Fixture
```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

# test_api.py
def test_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
```

---

## Testing HTTP Methods

### GET Request
```python
def test_get(client):
    response = client.get("/items/1")
    assert response.status_code == 200
```

### POST Request
```python
def test_post(client):
    response = client.post(
        "/items/",
        json={"name": "Test Item", "price": 10.5}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Item"
```

### PUT Request
```python
def test_put(client):
    response = client.put(
        "/items/1",
        json={"name": "Updated Item", "price": 15.0}
    )
    assert response.status_code == 200
```

### PATCH Request
```python
def test_patch(client):
    response = client.patch(
        "/items/1",
        json={"price": 20.0}
    )
    assert response.status_code == 200
```

### DELETE Request
```python
def test_delete(client):
    response = client.delete("/items/1")
    assert response.status_code == 204
```

---

## Request Patterns

### Query Parameters
```python
def test_query_params(client):
    response = client.get("/items/?skip=0&limit=10")
    assert response.status_code == 200

    response = client.get("/search", params={"q": "test", "page": 1})
    assert response.status_code == 200
```

### Path Parameters
```python
def test_path_params(client):
    response = client.get("/users/123/items/456")
    assert response.status_code == 200
```

### Headers
```python
def test_headers(client):
    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer token123"}
    )
    assert response.status_code == 200
```

### Cookies
```python
def test_cookies(client):
    response = client.get(
        "/dashboard",
        cookies={"session_id": "abc123"}
    )
    assert response.status_code == 200
```

### Form Data
```python
def test_form(client):
    response = client.post(
        "/login",
        data={"username": "user", "password": "pass"}
    )
    assert response.status_code == 200
```

### File Upload
```python
def test_file_upload(client):
    with open("test.txt", "rb") as f:
        response = client.post(
            "/upload",
            files={"file": ("test.txt", f, "text/plain")}
        )
    assert response.status_code == 200

def test_multiple_files(client):
    files = [
        ("files", ("file1.txt", b"content1", "text/plain")),
        ("files", ("file2.txt", b"content2", "text/plain")),
    ]
    response = client.post("/upload-multiple", files=files)
    assert response.status_code == 200
```

### Response Assertions
```python
def test_response(client):
    response = client.get("/item/1")

    # Status code
    assert response.status_code == 200

    # JSON body
    data = response.json()
    assert data["id"] == 1

    # Headers
    assert response.headers["content-type"] == "application/json"

    # Cookies
    assert "session" in response.cookies
```

---

## Dependency Overrides

### Basic Override
```python
from fastapi import Depends
from app.main import app
from app.dependencies import get_db

def get_db_override():
    return MockDatabase()

app.dependency_overrides[get_db] = get_db_override
```

### Override in Fixture
```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_current_user

@pytest.fixture
def client():
    def override_get_current_user():
        return {"id": 1, "username": "testuser"}

    app.dependency_overrides[get_current_user] = override_get_current_user
    yield TestClient(app)
    app.dependency_overrides.clear()
```

### Override with Parameters
```python
@pytest.fixture
def authenticated_client(client):
    def override_user():
        return User(id=1, role="admin")

    app.dependency_overrides[get_current_user] = override_user
    yield client
    app.dependency_overrides.clear()
```

### Override External Services
```python
# Original dependency
async def get_weather_service():
    return WeatherAPIClient()

# Test override
def mock_weather_service():
    mock = MagicMock()
    mock.get_temperature.return_value = 25.0
    return mock

app.dependency_overrides[get_weather_service] = mock_weather_service
```

---

## Async Testing

### Installation
```bash
pip install pytest-anyio httpx
```

### Async Test with AsyncClient
```python
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app

@pytest.mark.anyio
async def test_async_root():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/")
        assert response.status_code == 200
```

### Async Fixture
```python
@pytest.fixture
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

@pytest.mark.anyio
async def test_with_fixture(async_client):
    response = await async_client.get("/")
    assert response.status_code == 200
```

### Testing Async Database Operations
```python
@pytest.mark.anyio
async def test_async_db(async_client, async_session):
    # Create test data
    user = User(name="Test")
    async_session.add(user)
    await async_session.commit()

    # Test endpoint
    response = await async_client.get(f"/users/{user.id}")
    assert response.status_code == 200
```

---

## Database Testing

### SQLModel with In-Memory SQLite
```python
import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_session

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
```

### Test with Pre-populated Data
```python
def test_get_items(client, session):
    # Setup test data
    item = Item(name="Test", price=10.0)
    session.add(item)
    session.commit()
    session.refresh(item)

    # Test
    response = client.get(f"/items/{item.id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test"
```

### Async Database Testing
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
async def async_session():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
```

### Transaction Rollback Pattern
```python
@pytest.fixture
def session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
```

---

## Authentication Testing

### Testing Protected Endpoints
```python
def test_protected_endpoint_unauthorized(client):
    response = client.get("/protected")
    assert response.status_code == 401

def test_protected_endpoint_authorized(client):
    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 200
```

### Mock Authentication
```python
@pytest.fixture
def authenticated_client():
    def override_auth():
        return User(id=1, username="test", role="user")

    app.dependency_overrides[get_current_user] = override_auth
    yield TestClient(app)
    app.dependency_overrides.clear()
```

### OAuth2 Testing
```python
def test_login(client):
    response = client.post(
        "/token",
        data={
            "username": "testuser",
            "password": "testpass",
            "grant_type": "password"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### Role-Based Testing
```python
@pytest.fixture
def admin_client():
    def override():
        return User(id=1, role="admin")
    app.dependency_overrides[get_current_user] = override
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def user_client():
    def override():
        return User(id=2, role="user")
    app.dependency_overrides[get_current_user] = override
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_admin_only(admin_client, user_client):
    assert admin_client.delete("/users/1").status_code == 200
    assert user_client.delete("/users/1").status_code == 403
```

---

## WebSocket Testing

### Basic WebSocket Test
```python
def test_websocket(client):
    with client.websocket_connect("/ws") as websocket:
        websocket.send_text("hello")
        data = websocket.receive_text()
        assert data == "Message: hello"
```

### WebSocket with JSON
```python
def test_websocket_json(client):
    with client.websocket_connect("/ws") as websocket:
        websocket.send_json({"type": "message", "content": "hello"})
        data = websocket.receive_json()
        assert data["status"] == "received"
```

### WebSocket Authentication
```python
def test_websocket_auth(client):
    with client.websocket_connect(
        "/ws",
        headers={"Authorization": "Bearer token"}
    ) as websocket:
        data = websocket.receive_json()
        assert data["authenticated"] is True
```

---

## Background Tasks Testing

### Testing Background Task Execution
```python
from unittest.mock import patch, MagicMock

def test_background_task(client):
    with patch("app.tasks.send_email") as mock_send:
        response = client.post(
            "/register",
            json={"email": "test@example.com"}
        )
        assert response.status_code == 200
        mock_send.assert_called_once_with("test@example.com")
```

### Testing with Task Queue
```python
@pytest.fixture
def mock_queue():
    queue = []

    def add_task(func, *args, **kwargs):
        queue.append((func, args, kwargs))

    return queue, add_task

def test_queued_task(client, mock_queue):
    queue, add_task = mock_queue
    with patch("app.main.background_tasks.add_task", add_task):
        response = client.post("/process")
        assert len(queue) == 1
```
