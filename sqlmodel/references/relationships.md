# SQLModel Relationships

## One-to-Many Relationship

Most common relationship: One parent has many children.

### Example: Team has many Heroes

```python
from sqlmodel import Field, Relationship, SQLModel

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str
    
    # Relationship attribute (not a database column)
    heroes: list["Hero"] = Relationship(back_populates="team")

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)
    
    # Foreign key (actual database column)
    team_id: int | None = Field(default=None, foreign_key="team.id")
    
    # Relationship attribute
    team: Team | None = Relationship(back_populates="heroes")
```

### Key Points

- `foreign_key="table.id"` creates the database column link
- `Relationship()` creates Python object navigation
- `back_populates` links both sides for bidirectional access
- Use `list["Hero"]` with quotes for forward references

### Creating Related Data

```python
from sqlmodel import Session

with Session(engine) as session:
    # Method 1: Create separately, link via foreign key
    team = Team(name="Preventers", headquarters="Sharp Tower")
    session.add(team)
    session.commit()
    
    hero = Hero(name="Deadpond", secret_name="Dive Wilson", team_id=team.id)
    session.add(hero)
    session.commit()
    
    # Method 2: Create together using relationship
    team = Team(name="Z-Force", headquarters="Sister Margaret's Bar")
    hero = Hero(name="Spider-Boy", secret_name="Pedro Parqueador", team=team)
    session.add(hero)  # Adds team automatically
    session.commit()
```

### Reading Related Data

```python
with Session(engine) as session:
    # Get hero's team
    hero = session.exec(select(Hero).where(Hero.name == "Spider-Boy")).first()
    print(f"Hero's team: {hero.team.name}")  # Automatic lazy loading
    
    # Get team's heroes
    team = session.exec(select(Team).where(Team.name == "Preventers")).first()
    print(f"Team heroes: {team.heroes}")  # Returns list
```

---

## Many-to-Many Relationship

When entities can have multiple connections to each other.

### Example: Heroes can belong to multiple Teams

```python
from sqlmodel import Field, Relationship, SQLModel

# Link table (association table)
class HeroTeamLink(SQLModel, table=True):
    team_id: int | None = Field(
        default=None, foreign_key="team.id", primary_key=True
    )
    hero_id: int | None = Field(
        default=None, foreign_key="hero.id", primary_key=True
    )

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str
    
    heroes: list["Hero"] = Relationship(
        back_populates="teams",
        link_model=HeroTeamLink  # Specifies the link table
    )

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)
    
    teams: list[Team] = Relationship(
        back_populates="heroes",
        link_model=HeroTeamLink
    )
```

### Creating Many-to-Many Data

```python
with Session(engine) as session:
    team_preventers = Team(name="Preventers", headquarters="Sharp Tower")
    team_zforce = Team(name="Z-Force", headquarters="Sister Margaret's Bar")
    
    hero_deadpond = Hero(
        name="Deadpond",
        secret_name="Dive Wilson",
        teams=[team_preventers, team_zforce]  # Multiple teams
    )
    
    hero_spiderboy = Hero(
        name="Spider-Boy",
        secret_name="Pedro Parqueador",
        teams=[team_preventers]
    )
    
    session.add(hero_deadpond)
    session.add(hero_spiderboy)
    session.commit()
```

### Reading Many-to-Many Data

```python
with Session(engine) as session:
    # Get hero's teams
    hero = session.exec(select(Hero).where(Hero.name == "Deadpond")).first()
    print(f"Deadpond's teams: {[t.name for t in hero.teams]}")
    
    # Get team's heroes
    team = session.exec(select(Team).where(Team.name == "Preventers")).first()
    print(f"Preventers heroes: {[h.name for h in team.heroes]}")
```

---

## Many-to-Many with Extra Fields

When the relationship itself has attributes.

### Example: Track if hero is training in team

```python
from sqlmodel import Field, Relationship, SQLModel

class HeroTeamLink(SQLModel, table=True):
    team_id: int | None = Field(
        default=None, foreign_key="team.id", primary_key=True
    )
    hero_id: int | None = Field(
        default=None, foreign_key="hero.id", primary_key=True
    )
    
    # Extra field on the relationship
    is_training: bool = False
    
    # Relationship attributes on the link itself
    team: "Team" = Relationship(back_populates="hero_links")
    hero: "Hero" = Relationship(back_populates="team_links")

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str
    
    # Now points to link objects, not heroes directly
    hero_links: list[HeroTeamLink] = Relationship(back_populates="team")

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)
    
    team_links: list[HeroTeamLink] = Relationship(back_populates="hero")
```

### Working with Extra Fields

```python
with Session(engine) as session:
    team = Team(name="Preventers", headquarters="Sharp Tower")
    hero = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
    
    session.add(team)
    session.add(hero)
    session.commit()
    session.refresh(team)
    session.refresh(hero)
    
    # Create link with extra field
    link = HeroTeamLink(team_id=team.id, hero_id=hero.id, is_training=True)
    session.add(link)
    session.commit()

# Query with extra field
with Session(engine) as session:
    team = session.exec(select(Team).where(Team.name == "Preventers")).first()
    for link in team.hero_links:
        print(f"Hero: {link.hero.name}, Training: {link.is_training}")
```

---

## Cascade Delete

Automatically delete related records.

```python
from sqlmodel import Field, Relationship, SQLModel

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    
    heroes: list["Hero"] = Relationship(
        back_populates="team",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    team_id: int | None = Field(default=None, foreign_key="team.id")
    team: Team | None = Relationship(back_populates="heroes")
```

With `cascade="all, delete-orphan"`:
- Deleting a team deletes all its heroes
- Removing a hero from `team.heroes` deletes the hero

---

## Eager Loading (Avoid N+1 Queries)

```python
from sqlmodel import select
from sqlalchemy.orm import selectinload, joinedload

# selectinload: Separate query for related objects (good for lists)
statement = select(Team).options(selectinload(Team.heroes))
teams = session.exec(statement).all()

# joinedload: Single query with JOIN (good for single objects)
statement = select(Hero).options(joinedload(Hero.team))
heroes = session.exec(statement).all()
```

---

## Relationship Summary

| Type | Pattern | Key Elements |
|------|---------|--------------|
| One-to-Many | Parent → Children | `foreign_key` on child, `Relationship` on both |
| Many-to-One | Child → Parent | Same as above, just different perspective |
| Many-to-Many | Both → Both | Link table with composite primary key, `link_model` parameter |
| M2M with Fields | Both → Link → Both | Relationships point to link model |
