---
name: sqlmodel
description: Comprehensive SQLModel skill for Python database development - from hello world to production. Use when building Python applications with SQL databases using SQLModel ORM. Triggers on requests involving SQLModel, Python database models, ORM patterns, FastAPI database integration, Pydantic database models, SQLAlchemy with type hints, database CRUD operations, relationships (one-to-many, many-to-many), Alembic migrations with SQLModel, async database sessions, or production database patterns.
---

# SQLModel Skill

SQLModel is a library for interacting with SQL databases from Python code using Python objects. It combines SQLAlchemy (ORM) and Pydantic (data validation) into a single model definition.

## Quick Start

### Installation

```bash
pip install sqlmodel
# For async support:
pip install sqlmodel aiosqlite  # SQLite async
pip install sqlmodel asyncpg    # PostgreSQL async
```

### Hello World

```python
from sqlmodel import Field, Session, SQLModel, create_engine, select

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: int | None = None

# Create engine and tables
engine = create_engine("sqlite:///database.db", echo=True)
SQLModel.metadata.create_all(engine)

# Create a hero
with Session(engine) as session:
    hero = Hero(name="Deadpond", secret_name="Dive Wilson")
    session.add(hero)
    session.commit()
    session.refresh(hero)
    print(f"Created hero: {hero}")

# Query heroes
with Session(engine) as session:
    statement = select(Hero).where(Hero.name == "Deadpond")
    hero = session.exec(statement).first()
    print(f"Found: {hero}")
```

## Core Concepts

### Model Definition

```python
from sqlmodel import Field, SQLModel

class Hero(SQLModel, table=True):
    # table=True makes this a database table (not just Pydantic model)
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)           # Indexed column
    secret_name: str
    age: int | None = Field(default=None)   # Optional field
```

### Field Options

| Option | Purpose |
|--------|---------|
| `primary_key=True` | Set as primary key |
| `index=True` | Create database index |
| `unique=True` | Unique constraint |
| `foreign_key="table.column"` | Foreign key reference |
| `default=value` | Default value |
| `nullable=True/False` | Allow NULL values |

### CRUD Operations

```python
from sqlmodel import Session, select

# CREATE
with Session(engine) as session:
    hero = Hero(name="Spider-Boy", secret_name="Pedro")
    session.add(hero)
    session.commit()
    session.refresh(hero)  # Get auto-generated id

# READ
with Session(engine) as session:
    # Single record
    hero = session.get(Hero, 1)  # By primary key
    
    # Query with filter
    statement = select(Hero).where(Hero.name == "Spider-Boy")
    hero = session.exec(statement).first()
    
    # All records
    heroes = session.exec(select(Hero)).all()
    
    # With limit/offset
    statement = select(Hero).offset(0).limit(10)
    heroes = session.exec(statement).all()

# UPDATE
with Session(engine) as session:
    hero = session.get(Hero, 1)
    hero.age = 25
    session.add(hero)
    session.commit()
    session.refresh(hero)

# DELETE
with Session(engine) as session:
    hero = session.get(Hero, 1)
    session.delete(hero)
    session.commit()
```

## Reference Files

For detailed patterns, see:

- **Relationships**: See [references/relationships.md](references/relationships.md) for one-to-many, many-to-many patterns
- **FastAPI Integration**: See [references/fastapi-integration.md](references/fastapi-integration.md) for API patterns
- **Migrations**: See [references/migrations.md](references/migrations.md) for Alembic setup
- **Production Patterns**: See [references/production-patterns.md](references/production-patterns.md) for async, testing, deployment
- **Learning Path**: See [references/learning-path.md](references/learning-path.md) for structured progression

## Common Patterns

### Multiple Models (API Safety)

```python
# Base model with shared fields
class HeroBase(SQLModel):
    name: str
    secret_name: str
    age: int | None = None

# Database table model
class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

# Create model (no id)
class HeroCreate(HeroBase):
    pass

# Public response model (hide secret_name if needed)
class HeroPublic(SQLModel):
    id: int
    name: str
    age: int | None = None

# Update model (all optional)
class HeroUpdate(SQLModel):
    name: str | None = None
    secret_name: str | None = None
    age: int | None = None
```

### Database URL Formats

```python
# SQLite
engine = create_engine("sqlite:///./database.db")

# PostgreSQL
engine = create_engine("postgresql://user:password@localhost:5432/dbname")

# MySQL
engine = create_engine("mysql+pymysql://user:password@localhost:3306/dbname")

# SQLite in-memory (testing)
engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
```

### Session Dependency (FastAPI)

```python
from fastapi import Depends, FastAPI
from sqlmodel import Session

def get_session():
    with Session(engine) as session:
        yield session

@app.get("/heroes/")
def read_heroes(session: Session = Depends(get_session)):
    return session.exec(select(Hero)).all()
```

## Key Points

1. **Single Model Definition**: One class for validation AND database
2. **Type Hints**: Full IDE support and type checking
3. **Pydantic Compatible**: Works with FastAPI response models
4. **SQLAlchemy Compatible**: Access raw SQLAlchemy when needed
5. **Async Support**: Via `sqlmodel.ext.asyncio.session.AsyncSession`

## When to Read Reference Files

| Task | Reference File |
|------|----------------|
| Setting up one-to-many or many-to-many | `relationships.md` |
| Building FastAPI endpoints | `fastapi-integration.md` |
| Database schema changes | `migrations.md` |
| Async sessions, testing, deployment | `production-patterns.md` |
| Learning SQLModel systematically | `learning-path.md` |
