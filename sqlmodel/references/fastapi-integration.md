# SQLModel with FastAPI Integration

SQLModel was designed specifically to work seamlessly with FastAPI.

## Basic Setup

```python
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

# Database setup
DATABASE_URL = "sqlite:///./database.db"
connect_args = {"check_same_thread": False}  # Required for SQLite
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Session dependency
def get_session():
    with Session(engine) as session:
        yield session

# FastAPI app
app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
```

---

## Multiple Models Pattern

Separate models for different API operations:

```python
from sqlmodel import Field, SQLModel

# Base model - shared fields
class HeroBase(SQLModel):
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)

# Database table model
class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

# Create request model (no id)
class HeroCreate(HeroBase):
    pass

# Public response model
class HeroPublic(HeroBase):
    id: int

# Update request model (all optional)
class HeroUpdate(SQLModel):
    name: str | None = None
    secret_name: str | None = None
    age: int | None = None
```

---

## CRUD Endpoints

### Create

```python
@app.post("/heroes/", response_model=HeroPublic)
def create_hero(hero: HeroCreate, session: Session = Depends(get_session)):
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero
```

### Read (List with Pagination)

```python
@app.get("/heroes/", response_model=list[HeroPublic])
def read_heroes(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100)
):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes
```

### Read (Single)

```python
@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, session: Session = Depends(get_session)):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero
```

### Update (Partial)

```python
@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(
    hero_id: int,
    hero: HeroUpdate,
    session: Session = Depends(get_session)
):
    db_hero = session.get(Hero, hero_id)
    if not db_hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    
    hero_data = hero.model_dump(exclude_unset=True)
    db_hero.sqlmodel_update(hero_data)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero
```

### Delete

```python
@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int, session: Session = Depends(get_session)):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}
```

---

## Relationships in API Responses

### Response Models with Relationships

```python
class TeamBase(SQLModel):
    name: str
    headquarters: str

class Team(TeamBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    heroes: list["Hero"] = Relationship(back_populates="team")

class HeroBase(SQLModel):
    name: str
    secret_name: str

class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    team_id: int | None = Field(default=None, foreign_key="team.id")
    team: Team | None = Relationship(back_populates="heroes")

# Response models (non-table, include related data)
class HeroPublicWithTeam(HeroBase):
    id: int
    team: TeamBase | None = None

class TeamPublicWithHeroes(TeamBase):
    id: int
    heroes: list[HeroBase] = []
```

### Endpoint with Relationships

```python
@app.get("/heroes/{hero_id}", response_model=HeroPublicWithTeam)
def read_hero_with_team(hero_id: int, session: Session = Depends(get_session)):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero

@app.get("/teams/{team_id}", response_model=TeamPublicWithHeroes)
def read_team_with_heroes(team_id: int, session: Session = Depends(get_session)):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team
```

---

## Typed Session Dependency (Modern Pattern)

```python
from typing import Annotated
from fastapi import Depends

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@app.get("/heroes/")
def read_heroes(session: SessionDep) -> list[Hero]:
    return session.exec(select(Hero)).all()
```

---

## Complete Example

```python
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

# Models
class HeroBase(SQLModel):
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)

class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class HeroCreate(HeroBase):
    pass

class HeroPublic(HeroBase):
    id: int

class HeroUpdate(SQLModel):
    name: str | None = None
    secret_name: str | None = None
    age: int | None = None

# Database
DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

# App
app = FastAPI()

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.post("/heroes/", response_model=HeroPublic)
def create_hero(hero: HeroCreate, session: SessionDep):
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero

@app.get("/heroes/", response_model=list[HeroPublic])
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=100, le=100)
):
    return session.exec(select(Hero).offset(offset).limit(limit)).all()

@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero

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

@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}
```

Run with: `uvicorn main:app --reload`

API docs at: `http://localhost:8000/docs`
