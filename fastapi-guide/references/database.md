# Database Integration with SQLModel

## Installation

```bash
pip install sqlmodel
```

## Define Models

```python
from typing import Optional
from sqlmodel import Field, SQLModel

# Base model for shared attributes
class HeroBase(SQLModel):
    name: str = Field(index=True)
    age: Optional[int] = Field(default=None, index=True)

# Table model (for database)
class Hero(HeroBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    secret_name: str

# Request models (for API)
class HeroCreate(HeroBase):
    secret_name: str

class HeroUpdate(SQLModel):
    name: Optional[str] = None
    age: Optional[int] = None
    secret_name: Optional[str] = None

# Response model
class HeroPublic(HeroBase):
    id: int
```

## Database Engine and Session

```python
from sqlmodel import create_engine, Session

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# check_same_thread=False needed for SQLite with FastAPI
engine = create_engine(
    sqlite_url,
    echo=True,  # Log SQL statements (disable in production)
    connect_args={"check_same_thread": False}
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

## Session Dependency

```python
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
```

## CRUD Operations

```python
from fastapi import FastAPI, HTTPException, Query
from sqlmodel import select

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Create
@app.post("/heroes/", response_model=HeroPublic)
def create_hero(hero: HeroCreate, session: SessionDep):
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero

# Read all with pagination
@app.get("/heroes/", response_model=list[HeroPublic])
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=100, le=100)
):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes

# Read one
@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero

# Update
@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero: HeroUpdate, session: SessionDep):
    db_hero = session.get(Hero, hero_id)
    if not db_hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    hero_data = hero.model_dump(exclude_unset=True)
    db_hero.sqlmodel_update(hero_data)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero

# Delete
@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}
```

## Relationships

```python
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str

    heroes: List["Hero"] = Relationship(back_populates="team")

class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: Optional[int] = Field(default=None, index=True)

    team_id: Optional[int] = Field(default=None, foreign_key="team.id")
    team: Optional[Team] = Relationship(back_populates="heroes")
```

## Querying with Relationships

```python
from sqlmodel import select

# Query with join
@app.get("/heroes/", response_model=list[HeroWithTeam])
def read_heroes(session: SessionDep):
    statement = select(Hero, Team).join(Team, isouter=True)
    results = session.exec(statement).all()
    return results

# Filter by relationship
@app.get("/teams/{team_id}/heroes", response_model=list[HeroPublic])
def read_team_heroes(team_id: int, session: SessionDep):
    statement = select(Hero).where(Hero.team_id == team_id)
    heroes = session.exec(statement).all()
    return heroes
```

## PostgreSQL Configuration

```python
# For PostgreSQL
from sqlmodel import create_engine

DATABASE_URL = "postgresql://user:password@localhost/dbname"
engine = create_engine(DATABASE_URL, echo=True)
```

## Async Database (SQLAlchemy Async)

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

@app.get("/heroes/")
async def read_heroes(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Hero))
    return result.scalars().all()
```

## Lifespan for Database Setup

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    yield
    # Shutdown (cleanup if needed)

app = FastAPI(lifespan=lifespan)
```

## Alembic Migrations

```bash
# Install
pip install alembic

# Initialize
alembic init alembic

# Edit alembic/env.py to use SQLModel metadata
# target_metadata = SQLModel.metadata

# Create migration
alembic revision --autogenerate -m "Create heroes table"

# Apply migration
alembic upgrade head
```
