# Production Testing Patterns

## Table of Contents
1. [Project Structure](#project-structure)
2. [Coverage Configuration](#coverage-configuration)
3. [CI/CD Integration](#cicd-integration)
4. [Test Organization](#test-organization)
5. [Mocking Strategies](#mocking-strategies)
6. [Performance Testing](#performance-testing)
7. [Error Handling Tests](#error-handling-tests)
8. [Best Practices](#best-practices)

---

## Project Structure

### Recommended Layout
```
project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── dependencies.py
│   └── routers/
│       ├── __init__.py
│       ├── users.py
│       └── items.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   └── test_schemas.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_users_api.py
│   │   └── test_items_api.py
│   └── e2e/
│       ├── __init__.py
│       └── test_workflows.py
├── pyproject.toml
└── pytest.ini
```

### conftest.py Hierarchy
```python
# tests/conftest.py - Shared fixtures for all tests
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from app.main import app
from app.database import get_session

@pytest.fixture(scope="session")
def engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

@pytest.fixture(scope="session", autouse=True)
def create_tables(engine):
    SQLModel.metadata.create_all(engine)

@pytest.fixture
def session(engine):
    with Session(engine) as session:
        yield session
        session.rollback()

@pytest.fixture
def client(session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    yield TestClient(app)
    app.dependency_overrides.clear()
```

---

## Coverage Configuration

### pyproject.toml
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "-v",
    "--strict-markers",
    "--cov=app",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-fail-under=80",
]
markers = [
    "slow: marks tests as slow",
    "integration: integration tests",
    "e2e: end-to-end tests",
]

[tool.coverage.run]
source = ["app"]
branch = true
omit = [
    "*/tests/*",
    "*/__init__.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
]
show_missing = true
fail_under = 80
```

### .coveragerc (Alternative)
```ini
[run]
source = app
branch = True
omit =
    */tests/*
    */__init__.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
show_missing = True
fail_under = 80

[html]
directory = htmlcov
```

### Running Coverage
```bash
# Basic coverage
pytest --cov=app

# With HTML report
pytest --cov=app --cov-report=html

# Fail if below threshold
pytest --cov=app --cov-fail-under=80

# Multiple report formats
pytest --cov=app --cov-report=term --cov-report=xml --cov-report=html
```

---

## CI/CD Integration

### GitHub Actions
```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[test]"

      - name: Run tests
        run: pytest --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

### GitLab CI
```yaml
# .gitlab-ci.yml
stages:
  - test

test:
  stage: test
  image: python:3.11
  before_script:
    - pip install -e ".[test]"
  script:
    - pytest --cov=app --cov-report=xml --junitxml=report.xml
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      junit: report.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

---

## Test Organization

### Test Categories
```python
# tests/conftest.py
def pytest_configure(config):
    config.addinivalue_line("markers", "unit: unit tests")
    config.addinivalue_line("markers", "integration: integration tests")
    config.addinivalue_line("markers", "e2e: end-to-end tests")
    config.addinivalue_line("markers", "slow: slow tests")
```

### Running Test Categories
```bash
# Unit tests only
pytest -m "unit"

# Integration tests
pytest -m "integration"

# Exclude slow tests
pytest -m "not slow"

# Unit and integration, not e2e
pytest -m "unit or integration" -m "not e2e"
```

### Test Naming Conventions
```python
# test_<module>_<function>_<scenario>
def test_create_user_with_valid_data():
    pass

def test_create_user_with_duplicate_email():
    pass

def test_get_user_not_found():
    pass

def test_delete_user_unauthorized():
    pass
```

---

## Mocking Strategies

### External API Mocking
```python
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_external_api():
    with patch("app.services.external_api.client") as mock:
        mock.get_data.return_value = {"status": "ok"}
        yield mock

def test_with_external_api(client, mock_external_api):
    response = client.get("/external-data")
    assert response.status_code == 200
    mock_external_api.get_data.assert_called_once()
```

### Time Mocking
```python
from freezegun import freeze_time

@freeze_time("2024-01-15 10:00:00")
def test_time_dependent(client):
    response = client.get("/current-time")
    assert response.json()["date"] == "2024-01-15"
```

### Environment Variable Mocking
```python
def test_config(client, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("DEBUG", "true")
    # Test with modified environment
```

### Response Mocking with respx
```python
import respx
import httpx

@respx.mock
def test_external_http(client):
    respx.get("https://api.example.com/data").mock(
        return_value=httpx.Response(200, json={"result": "ok"})
    )
    response = client.get("/fetch-external")
    assert response.status_code == 200
```

---

## Performance Testing

### Response Time Testing
```python
import time

def test_response_time(client):
    start = time.perf_counter()
    response = client.get("/api/items")
    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 0.5  # 500ms threshold
```

### Load Testing with pytest-benchmark
```python
def test_endpoint_performance(client, benchmark):
    def call_endpoint():
        return client.get("/api/items")

    result = benchmark(call_endpoint)
    assert result.status_code == 200
```

### Concurrent Request Testing
```python
import asyncio
import httpx

@pytest.mark.anyio
async def test_concurrent_requests():
    async with httpx.AsyncClient(base_url="http://test") as client:
        tasks = [client.get("/api/items") for _ in range(100)]
        responses = await asyncio.gather(*tasks)

        assert all(r.status_code == 200 for r in responses)
```

---

## Error Handling Tests

### HTTP Error Codes
```python
def test_not_found(client):
    response = client.get("/items/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

def test_validation_error(client):
    response = client.post("/items/", json={"name": ""})
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(e["loc"] == ["body", "name"] for e in errors)

def test_unauthorized(client):
    response = client.get("/protected")
    assert response.status_code == 401

def test_forbidden(user_client):
    response = user_client.delete("/admin/users/1")
    assert response.status_code == 403
```

### Exception Handling
```python
from unittest.mock import patch

def test_internal_error_handling(client):
    with patch("app.services.process_data") as mock:
        mock.side_effect = Exception("Database error")
        response = client.post("/process")
        assert response.status_code == 500
        assert "error" in response.json()
```

### Validation Edge Cases
```python
@pytest.mark.parametrize("invalid_email", [
    "",
    "notanemail",
    "@nodomain.com",
    "missing@.com",
    "a" * 256 + "@test.com",
])
def test_email_validation(client, invalid_email):
    response = client.post(
        "/users/",
        json={"email": invalid_email, "name": "Test"}
    )
    assert response.status_code == 422
```

---

## Best Practices

### Test Isolation
```python
# Each test gets fresh database state
@pytest.fixture(autouse=True)
def reset_db(session):
    yield
    session.rollback()
    for table in reversed(SQLModel.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
```

### Factory Pattern for Test Data
```python
# tests/factories.py
from faker import Faker

fake = Faker()

def create_user_data(**overrides):
    return {
        "email": fake.email(),
        "name": fake.name(),
        "password": fake.password(),
        **overrides
    }

def create_item_data(**overrides):
    return {
        "name": fake.word(),
        "description": fake.sentence(),
        "price": fake.pydecimal(min_value=1, max_value=1000),
        **overrides
    }

# In tests
def test_create_user(client):
    data = create_user_data(email="specific@test.com")
    response = client.post("/users/", json=data)
    assert response.status_code == 201
```

### Assertion Helpers
```python
# tests/helpers.py
def assert_user_response(response, expected_email):
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["email"] == expected_email
    assert "password" not in data  # Ensure password not exposed

def assert_paginated_response(response, expected_count=None):
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    if expected_count:
        assert len(data["items"]) == expected_count
```

### Parallel Test Execution
```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto  # Auto-detect CPU count
pytest -n 4     # Use 4 workers
```

### Test Configuration for Parallel Execution
```python
# conftest.py
@pytest.fixture(scope="session")
def worker_id(request):
    """Get unique worker ID for parallel test isolation."""
    if hasattr(request.config, "workerinput"):
        return request.config.workerinput["workerid"]
    return "master"

@pytest.fixture(scope="session")
def database_url(worker_id):
    """Unique database per worker for parallel execution."""
    return f"sqlite:///test_{worker_id}.db"
```

### Debugging Failed Tests
```bash
# Stop on first failure
pytest -x

# Enter debugger on failure
pytest --pdb

# Show local variables in traceback
pytest -l

# Verbose output
pytest -vv

# Show print statements
pytest -s

# Run last failed tests
pytest --lf

# Run failed tests first
pytest --ff
```
