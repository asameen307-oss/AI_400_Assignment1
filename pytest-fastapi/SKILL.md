---
name: pytest-fastapi
description: |
  Complete pytest testing guide for FastAPI applications, from hello world to production-grade testing.
  Use this skill when: (1) Writing tests for FastAPI endpoints, (2) Setting up pytest fixtures for FastAPI,
  (3) Testing with database/dependency overrides, (4) Implementing async tests, (5) Configuring coverage
  and CI/CD pipelines, (6) Learning pytest patterns (fixtures, parametrization, markers), (7) Testing
  authentication, WebSockets, or background tasks. Covers TestClient, AsyncClient, SQLModel testing,
  mocking, and production best practices.
---

# Pytest for FastAPI Testing

## Quick Start

### Installation
```bash
pip install pytest httpx pytest-cov
```

### Hello World Test
```python
# test_main.py
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

Run: `pytest test_main.py -v`

---

## Core Workflow

### 1. Project Setup

Create test directory and conftest.py:
```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)
```

### 2. Basic API Testing
```python
# tests/test_api.py
def test_get_items(client):
    response = client.get("/items/")
    assert response.status_code == 200

def test_create_item(client):
    response = client.post("/items/", json={"name": "Test", "price": 10.0})
    assert response.status_code == 201
    assert response.json()["name"] == "Test"
```

### 3. Dependency Overrides
```python
# tests/conftest.py
from app.dependencies import get_db

@pytest.fixture
def client(session):
    def override_get_db():
        return session
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

### 4. Database Testing with SQLModel
```python
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
```

### 5. Run Tests with Coverage
```bash
pytest --cov=app --cov-report=term-missing
```

---

## Reference Files

### Pytest Core Patterns
See [references/pytest-core.md](references/pytest-core.md) for:
- Fixtures (scope, yield, factory, autouse)
- Parametrization patterns
- Markers (skip, skipif, xfail, custom)
- Assertions (raises, approx, warns)
- Monkeypatch (attributes, env vars, dicts)
- Temporary files (tmp_path)
- Logging capture (caplog)
- Configuration (pyproject.toml, CLI options)

### FastAPI Testing Patterns
See [references/fastapi-testing.md](references/fastapi-testing.md) for:
- TestClient usage (all HTTP methods)
- Request patterns (headers, cookies, files, forms)
- Dependency overrides
- Async testing with AsyncClient
- Database testing patterns
- Authentication testing
- WebSocket testing
- Background tasks testing

### Production Patterns
See [references/production-patterns.md](references/production-patterns.md) for:
- Project structure
- Coverage configuration
- CI/CD integration (GitHub Actions, GitLab CI)
- Test organization and categories
- Mocking strategies
- Performance testing
- Error handling tests
- Best practices (isolation, factories, parallel execution)

---

## Common Patterns

### Authenticated Endpoint Testing
```python
@pytest.fixture
def auth_client():
    def override_user():
        return User(id=1, role="admin")
    app.dependency_overrides[get_current_user] = override_user
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_protected(auth_client):
    response = auth_client.get("/protected")
    assert response.status_code == 200
```

### Parametrized Tests
```python
@pytest.mark.parametrize("item_id,expected_status", [
    (1, 200),
    (999, 404),
])
def test_get_item(client, item_id, expected_status):
    response = client.get(f"/items/{item_id}")
    assert response.status_code == expected_status
```

### Async Testing
```python
import pytest
from httpx import ASGITransport, AsyncClient

@pytest.mark.anyio
async def test_async():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/")
        assert response.status_code == 200
```

---

## Configuration

### pyproject.toml
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["-v", "--strict-markers", "--cov=app"]
markers = [
    "slow: slow tests",
    "integration: integration tests",
]

[tool.coverage.run]
source = ["app"]
branch = true

[tool.coverage.report]
fail_under = 80
```

### Running Tests
```bash
pytest                      # All tests
pytest -v                   # Verbose
pytest -x                   # Stop on first failure
pytest -k "test_create"     # Match pattern
pytest -m "not slow"        # Exclude marker
pytest --lf                 # Last failed
pytest -n auto              # Parallel (requires pytest-xdist)
```
