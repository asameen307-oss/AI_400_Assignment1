# Pytest Core Reference

## Table of Contents
1. [Basic Test Structure](#basic-test-structure)
2. [Fixtures](#fixtures)
3. [Parametrization](#parametrization)
4. [Markers](#markers)
5. [Assertions](#assertions)
6. [Monkeypatch](#monkeypatch)
7. [Temporary Files](#temporary-files)
8. [Logging Capture](#logging-capture)
9. [Configuration](#configuration)

---

## Basic Test Structure

### Hello World Test
```python
# test_hello.py
def test_hello():
    assert 1 + 1 == 2
```

Run with: `pytest` or `pytest test_hello.py -v`

### Test Discovery Rules
- Files: `test_*.py` or `*_test.py`
- Functions: `test_*`
- Classes: `Test*` (no `__init__` method)

---

## Fixtures

### Basic Fixture
```python
import pytest

@pytest.fixture
def sample_data():
    return {"name": "test", "value": 42}

def test_with_fixture(sample_data):
    assert sample_data["name"] == "test"
```

### Fixture Scopes
```python
@pytest.fixture(scope="function")  # Default: new for each test
def func_fixture(): ...

@pytest.fixture(scope="class")     # Per test class
def class_fixture(): ...

@pytest.fixture(scope="module")    # Per module
def module_fixture(): ...

@pytest.fixture(scope="session")   # Once per test session
def session_fixture(): ...
```

### Yield Fixtures (Setup/Teardown)
```python
@pytest.fixture
def db_connection():
    conn = create_connection()
    yield conn
    conn.close()  # Teardown runs after test
```

### Factory Fixtures
```python
@pytest.fixture
def make_user():
    created_users = []

    def _make_user(name, email):
        user = User(name=name, email=email)
        created_users.append(user)
        return user

    yield _make_user

    for user in created_users:
        user.delete()

def test_multiple_users(make_user):
    user1 = make_user("Alice", "alice@test.com")
    user2 = make_user("Bob", "bob@test.com")
    assert user1.name != user2.name
```

### Autouse Fixtures
```python
@pytest.fixture(autouse=True)
def setup_logging(caplog):
    caplog.set_level(logging.DEBUG)
```

### Fixture Dependencies
```python
@pytest.fixture
def base_config():
    return {"debug": True}

@pytest.fixture
def app_config(base_config):
    return {**base_config, "name": "test_app"}
```

### conftest.py Fixtures
```python
# conftest.py - fixtures available to all tests in directory
import pytest

@pytest.fixture
def api_client():
    return TestClient(app)
```

---

## Parametrization

### Basic Parametrization
```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    assert input * 2 == expected
```

### Multiple Parameters
```python
@pytest.mark.parametrize("x", [1, 2])
@pytest.mark.parametrize("y", [10, 20])
def test_combinations(x, y):
    # Runs: (1,10), (1,20), (2,10), (2,20)
    assert x + y > 0
```

### Named Test IDs
```python
@pytest.mark.parametrize("input,expected", [
    pytest.param(1, 2, id="one"),
    pytest.param(2, 4, id="two"),
])
def test_named(input, expected):
    assert input * 2 == expected
```

### Parametrized Fixtures
```python
@pytest.fixture(params=["sqlite", "postgres", "mysql"])
def database(request):
    db = connect_db(request.param)
    yield db
    db.close()

def test_query(database):
    # Runs 3 times with different databases
    result = database.query("SELECT 1")
    assert result is not None
```

### Conditional Parametrization
```python
@pytest.mark.parametrize("value", [
    1,
    pytest.param(2, marks=pytest.mark.skip(reason="not ready")),
    pytest.param(3, marks=pytest.mark.xfail),
])
def test_values(value):
    assert value > 0
```

---

## Markers

### Built-in Markers
```python
@pytest.mark.skip(reason="Not implemented")
def test_skip(): ...

@pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires Python 3.10+")
def test_skipif(): ...

@pytest.mark.xfail(reason="Known bug")
def test_expected_failure(): ...

@pytest.mark.usefixtures("setup_db")
def test_with_fixtures(): ...
```

### Custom Markers
```python
# conftest.py
def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: integration tests")

# test_example.py
@pytest.mark.slow
def test_slow_operation(): ...

@pytest.mark.integration
def test_api_integration(): ...
```

Run specific markers: `pytest -m "slow"` or `pytest -m "not slow"`

### Register in pyproject.toml
```toml
[tool.pytest.ini_options]
markers = [
    "slow: marks tests as slow",
    "integration: integration tests",
]
```

---

## Assertions

### Basic Assertions
```python
def test_assertions():
    assert value == expected
    assert value != other
    assert value > 0
    assert value in collection
    assert isinstance(obj, MyClass)
```

### Approximate Comparisons
```python
def test_float():
    assert 0.1 + 0.2 == pytest.approx(0.3)
    assert [0.1 + 0.2, 0.2 + 0.4] == pytest.approx([0.3, 0.6])
```

### Exception Testing
```python
def test_raises():
    with pytest.raises(ValueError):
        raise ValueError("error")

def test_raises_match():
    with pytest.raises(ValueError, match=r"invalid.*value"):
        raise ValueError("invalid input value")

def test_raises_info():
    with pytest.raises(ValueError) as exc_info:
        raise ValueError("test error")
    assert "test" in str(exc_info.value)
```

### Warning Testing
```python
def test_warning():
    with pytest.warns(DeprecationWarning):
        deprecated_function()

def test_warning_match():
    with pytest.warns(UserWarning, match="will be removed"):
        warn_user()
```

---

## Monkeypatch

### Patching Attributes
```python
def test_patch_attr(monkeypatch):
    monkeypatch.setattr(requests, "get", mock_get)
    response = requests.get("http://example.com")
```

### Patching Environment Variables
```python
def test_env_var(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")
    assert os.environ["API_KEY"] == "test-key"

def test_del_env(monkeypatch):
    monkeypatch.delenv("SECRET", raising=False)
```

### Patching Dictionary Items
```python
def test_dict_patch(monkeypatch):
    monkeypatch.setitem(config, "debug", True)
    monkeypatch.delitem(config, "unused_key", raising=False)
```

### Patching with Context
```python
def test_context_patch(monkeypatch):
    with monkeypatch.context() as m:
        m.setattr(module, "value", 42)
        assert module.value == 42
    # Original value restored here
```

---

## Temporary Files

### tmp_path Fixture
```python
def test_file_operations(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("hello")
    assert file.read_text() == "hello"
```

### tmp_path_factory (Session Scope)
```python
@pytest.fixture(scope="session")
def shared_data_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("data")
```

---

## Logging Capture

### caplog Fixture
```python
def test_logging(caplog):
    caplog.set_level(logging.INFO)
    my_function()

    assert "expected message" in caplog.text
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "INFO"
```

### Assert on Log Records
```python
def test_log_records(caplog):
    with caplog.at_level(logging.WARNING):
        trigger_warning()

    assert caplog.record_tuples == [
        ("my.logger", logging.WARNING, "warning message")
    ]
```

---

## Configuration

### pyproject.toml
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
]
markers = [
    "slow: marks tests as slow",
    "integration: integration tests",
]
filterwarnings = [
    "ignore::DeprecationWarning",
]
```

### pytest.ini
```ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -v --strict-markers
markers =
    slow: marks tests as slow
    integration: integration tests
```

### Command Line Options
```bash
pytest -v                    # Verbose output
pytest -q                    # Quiet mode
pytest -x                    # Stop on first failure
pytest --lf                  # Run last failed tests
pytest --ff                  # Run failed first
pytest -k "test_name"        # Run tests matching pattern
pytest -m "marker"           # Run tests with marker
pytest --tb=short            # Short traceback
pytest --collect-only        # Show tests without running
pytest --fixtures            # Show available fixtures
```
