# SQLModel Production Patterns

## Async Sessions

For high-concurrency applications (FastAPI async endpoints).

### Setup

```bash
pip install sqlmodel aiosqlite  # SQLite async
pip install sqlmodel asyncpg    # PostgreSQL async
```

### Async Engine and Session

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel

# Async database URL (note the +aiosqlite or +asyncpg)
DATABASE_URL = "sqlite+aiosqlite:///./database.db"
# DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/dbname"

# Create async engine
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set False in production
    future=True,
)

# Create async session factory
async_session = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Create tables (run synchronously within async context)
async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

### FastAPI Async Integration

```python
from typing import AsyncGenerator, Annotated
from fastapi import Depends, FastAPI
from sqlmodel import select

app = FastAPI()

# Async session dependency
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/heroes/")
async def read_heroes(session: SessionDep):
    result = await session.exec(select(Hero))
    return result.all()

@app.post("/heroes/")
async def create_hero(hero: HeroCreate, session: SessionDep):
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    await session.commit()
    await session.refresh(db_hero)
    return db_hero
```

---

## Testing

### Test Setup with pytest

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app, get_session

@pytest.fixture(name="session")
def session_fixture():
    # In-memory SQLite for tests
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # Important for in-memory SQLite
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

### Test Examples

```python
# tests/test_heroes.py
from fastapi.testclient import TestClient
from sqlmodel import Session

def test_create_hero(client: TestClient):
    response = client.post(
        "/heroes/",
        json={"name": "Deadpond", "secret_name": "Dive Wilson"}
    )
    data = response.json()
    
    assert response.status_code == 200
    assert data["name"] == "Deadpond"
    assert data["secret_name"] == "Dive Wilson"
    assert data["id"] is not None

def test_read_hero(session: Session, client: TestClient):
    # Setup: Create hero directly in database
    hero = Hero(name="Spider-Boy", secret_name="Pedro")
    session.add(hero)
    session.commit()
    session.refresh(hero)
    
    # Test
    response = client.get(f"/heroes/{hero.id}")
    data = response.json()
    
    assert response.status_code == 200
    assert data["name"] == "Spider-Boy"

def test_read_hero_not_found(client: TestClient):
    response = client.get("/heroes/999")
    assert response.status_code == 404
```

### Async Testing

```python
# tests/conftest.py for async
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool  # Important for async tests
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.main import app, get_session

@pytest.fixture
async def async_session():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=NullPool,  # Prevents loop issues in tests
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    async_session_maker = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_maker() as session:
        yield session

@pytest.fixture
async def async_client(async_session):
    async def get_session_override():
        yield async_session
    
    app.dependency_overrides[get_session] = get_session_override
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()

# Test
@pytest.mark.asyncio
async def test_create_hero_async(async_client):
    response = await async_client.post(
        "/heroes/",
        json={"name": "Deadpond", "secret_name": "Dive Wilson"}
    )
    assert response.status_code == 200
```

---

## Environment Configuration

### Using Environment Variables

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./database.db"
    echo_sql: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()

# app/database.py
from sqlmodel import create_engine
from app.config import settings

engine = create_engine(
    settings.database_url,
    echo=settings.echo_sql,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)
```

```bash
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
ECHO_SQL=false
```

---

## Connection Pooling (PostgreSQL)

```python
from sqlmodel import create_engine

engine = create_engine(
    "postgresql://user:pass@localhost:5432/dbname",
    pool_size=5,           # Number of connections to keep
    max_overflow=10,       # Extra connections when pool exhausted
    pool_timeout=30,       # Seconds to wait for connection
    pool_recycle=1800,     # Recycle connections after 30 min
    pool_pre_ping=True,    # Verify connections before use
)
```

---

## Error Handling

```python
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

@app.post("/heroes/")
def create_hero(hero: HeroCreate, session: SessionDep):
    try:
        db_hero = Hero.model_validate(hero)
        session.add(db_hero)
        session.commit()
        session.refresh(db_hero)
        return db_hero
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail="Hero with this name already exists"
        )
```

---

## Soft Deletes

```python
from datetime import datetime
from sqlmodel import Field, SQLModel

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    deleted_at: datetime | None = Field(default=None)

# Query only active records
def get_active_heroes(session: Session):
    statement = select(Hero).where(Hero.deleted_at.is_(None))
    return session.exec(statement).all()

# Soft delete
def soft_delete_hero(session: Session, hero_id: int):
    hero = session.get(Hero, hero_id)
    if hero:
        hero.deleted_at = datetime.utcnow()
        session.add(hero)
        session.commit()
```

---

## Audit Fields

```python
from datetime import datetime
from sqlmodel import Field, SQLModel

class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Hero(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    secret_name: str

# Update timestamp on changes
@app.patch("/heroes/{hero_id}")
def update_hero(hero_id: int, hero: HeroUpdate, session: SessionDep):
    db_hero = session.get(Hero, hero_id)
    if not db_hero:
        raise HTTPException(status_code=404)
    
    hero_data = hero.model_dump(exclude_unset=True)
    hero_data["updated_at"] = datetime.utcnow()
    db_hero.sqlmodel_update(hero_data)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero
```

---

## Transactions

```python
from sqlmodel import Session

def transfer_hero(session: Session, hero_id: int, from_team_id: int, to_team_id: int):
    """Transfer hero between teams atomically."""
    try:
        hero = session.get(Hero, hero_id)
        from_team = session.get(Team, from_team_id)
        to_team = session.get(Team, to_team_id)
        
        if not all([hero, from_team, to_team]):
            raise ValueError("Invalid IDs")
        
        # Both operations in same transaction
        hero.team_id = to_team_id
        session.add(hero)
        session.commit()
        
    except Exception:
        session.rollback()
        raise
```

---

## Bulk Operations

```python
from sqlmodel import Session

# Bulk insert
def bulk_create_heroes(session: Session, heroes_data: list[dict]):
    heroes = [Hero(**data) for data in heroes_data]
    session.add_all(heroes)
    session.commit()

# Bulk update
def bulk_update_ages(session: Session, hero_ids: list[int], new_age: int):
    statement = (
        update(Hero)
        .where(Hero.id.in_(hero_ids))
        .values(age=new_age)
    )
    session.exec(statement)
    session.commit()
```

---

## Health Check Endpoint

```python
from sqlmodel import text

@app.get("/health")
def health_check(session: SessionDep):
    try:
        session.exec(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={"status": "unhealthy", "database": str(e)}
        )
```

---

## Production Checklist

- [ ] Use environment variables for database URL
- [ ] Set `echo=False` in production
- [ ] Configure connection pooling for PostgreSQL
- [ ] Use Alembic for migrations
- [ ] Add database health check endpoint
- [ ] Implement proper error handling
- [ ] Add audit fields (created_at, updated_at)
- [ ] Write tests with isolated test database
- [ ] Use async sessions for high concurrency
- [ ] Set up CI/CD pipeline with migration step
