# Testing FastAPI Applications

## Basic Testing with TestClient

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/")
async def read_root():
    return {"msg": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

# Tests
client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

def test_read_item():
    response = client.get("/items/42?q=test")
    assert response.status_code == 200
    assert response.json() == {"item_id": 42, "q": "test"}

def test_invalid_item():
    response = client.get("/items/invalid")
    assert response.status_code == 422  # Validation error
```

## Important: Use `def` Not `async def`

From official docs:
> Notice that the testing functions are normal `def`, not `async def`.
> And the calls to the client are also normal calls, not using `await`.
> This allows you to use `pytest` directly without complications.

## Testing with Dependencies Override

```python
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

async def get_db():
    return {"db": "production"}

@app.get("/items/")
async def read_items(db=Depends(get_db)):
    return db

# Test with override
def test_read_items():
    def override_get_db():
        return {"db": "test"}

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)
    response = client.get("/items/")
    assert response.json() == {"db": "test"}

    # Clean up
    app.dependency_overrides.clear()
```

## Testing with Database

```python
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

def test_create_hero():
    # Create in-memory test database
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def get_session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    response = client.post(
        "/heroes/",
        json={"name": "Deadpond", "secret_name": "Dive Wilson"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Deadpond"
    assert "id" in data

    app.dependency_overrides.clear()
```

## Testing POST with JSON Body

```python
def test_create_item():
    response = client.post(
        "/items/",
        json={"name": "Foo", "price": 45.0}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Foo"
```

## Testing with Headers

```python
def test_read_items_with_token():
    response = client.get(
        "/items/",
        headers={"X-Token": "secret-token"}
    )
    assert response.status_code == 200
```

## Testing Authentication

```python
def test_login():
    response = client.post(
        "/token",
        data={"username": "johndoe", "password": "secret"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Use token for authenticated request
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "johndoe"
```

## Testing File Upload

```python
def test_upload_file():
    response = client.post(
        "/uploadfile/",
        files={"file": ("test.txt", b"file content", "text/plain")}
    )
    assert response.status_code == 200
    assert response.json()["filename"] == "test.txt"
```

## Testing Form Data

```python
def test_login_form():
    response = client.post(
        "/login/",
        data={"username": "john", "password": "secret"}
    )
    assert response.status_code == 200
```

## Pytest Fixtures

```python
import pytest
from fastapi.testclient import TestClient
from main import app, get_session
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

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

def test_create_hero(client: TestClient):
    response = client.post(
        "/heroes/",
        json={"name": "Deadpond", "secret_name": "Dive Wilson"}
    )
    assert response.status_code == 200
```

## Running Tests

```bash
# Install pytest
pip install pytest httpx

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific file
pytest tests/test_main.py

# Run specific test
pytest tests/test_main.py::test_read_root

# Run with coverage
pip install pytest-cov
pytest --cov=app tests/
```

## Project Structure for Tests

```
project/
├── app/
│   ├── __init__.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py      # Shared fixtures
│   ├── test_main.py
│   └── test_users.py
└── pytest.ini
```

## pytest.ini Configuration

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v --tb=short
```
