# SQLModel Learning Path

Structured progression from beginner to production-ready, following Bloom's Taxonomy.

---

## Phase 1: Hello World (Bloom's Level 1-2: Remember & Understand)

**Goal**: Get SQLModel running and understand basic concepts.

### Step 1.1: Installation

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install sqlmodel
```

### Step 1.2: First Model

```python
# hello_sqlmodel.py
from sqlmodel import Field, SQLModel, Session, create_engine, select

# Define a model (table=True makes it a database table)
class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    power: str

# Create database engine
engine = create_engine("sqlite:///heroes.db", echo=True)

# Create tables
SQLModel.metadata.create_all(engine)

# Insert data
with Session(engine) as session:
    hero = Hero(name="Spider-Man", power="Web-slinging")
    session.add(hero)
    session.commit()
    print(f"Created: {hero}")

# Query data
with Session(engine) as session:
    heroes = session.exec(select(Hero)).all()
    print(f"All heroes: {heroes}")
```

Run: `python hello_sqlmodel.py`

### Checkpoint 1
- [ ] Can create a SQLModel class
- [ ] Understand `table=True` vs without it
- [ ] Can create engine and tables
- [ ] Can insert and query records

---

## Phase 2: Core Concepts (Bloom's Level 2-3: Understand & Apply)

**Goal**: Master CRUD operations and model configuration.

### Step 2.1: Field Options

```python
from sqlmodel import Field, SQLModel

class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)                    # Indexed for fast lookup
    sku: str = Field(unique=True)                    # Must be unique
    price: float = Field(ge=0)                       # Validation: >= 0
    description: str | None = Field(default=None)    # Optional field
    in_stock: bool = Field(default=True)             # Default value
```

### Step 2.2: Complete CRUD

```python
from sqlmodel import Session, select

# CREATE
def create_product(session: Session, name: str, sku: str, price: float) -> Product:
    product = Product(name=name, sku=sku, price=price)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

# READ - Single
def get_product(session: Session, product_id: int) -> Product | None:
    return session.get(Product, product_id)

# READ - List with filter
def get_products_in_stock(session: Session) -> list[Product]:
    statement = select(Product).where(Product.in_stock == True)
    return session.exec(statement).all()

# UPDATE
def update_price(session: Session, product_id: int, new_price: float) -> Product | None:
    product = session.get(Product, product_id)
    if product:
        product.price = new_price
        session.add(product)
        session.commit()
        session.refresh(product)
    return product

# DELETE
def delete_product(session: Session, product_id: int) -> bool:
    product = session.get(Product, product_id)
    if product:
        session.delete(product)
        session.commit()
        return True
    return False
```

### Step 2.3: Filtering and Ordering

```python
from sqlmodel import select, or_, and_

# Multiple conditions
statement = select(Product).where(
    and_(
        Product.price < 100,
        Product.in_stock == True
    )
)

# OR conditions
statement = select(Product).where(
    or_(
        Product.name.contains("Pro"),
        Product.price > 500
    )
)

# Ordering
statement = select(Product).order_by(Product.price.desc())

# Limit and offset (pagination)
statement = select(Product).offset(10).limit(5)
```

### Checkpoint 2
- [ ] Can use all Field options
- [ ] Can perform all CRUD operations
- [ ] Can filter with WHERE, AND, OR
- [ ] Can order and paginate results

---

## Phase 3: Mini Project - Task Manager (Bloom's Level 3: Apply)

**Goal**: Build a complete working application.

### Project Structure

```
task_manager/
├── models.py
├── database.py
├── crud.py
└── main.py
```

### Implementation

```python
# models.py
from datetime import datetime
from enum import Enum
from sqlmodel import Field, SQLModel

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str | None = None
    status: TaskStatus = Field(default=TaskStatus.TODO)
    priority: int = Field(default=1, ge=1, le=5)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    due_date: datetime | None = None
```

```python
# database.py
from sqlmodel import create_engine, SQLModel

DATABASE_URL = "sqlite:///tasks.db"
engine = create_engine(DATABASE_URL)

def init_db():
    SQLModel.metadata.create_all(engine)
```

```python
# crud.py
from sqlmodel import Session, select
from models import Task, TaskStatus

def create_task(session: Session, title: str, **kwargs) -> Task:
    task = Task(title=title, **kwargs)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

def get_tasks_by_status(session: Session, status: TaskStatus) -> list[Task]:
    return session.exec(select(Task).where(Task.status == status)).all()

def mark_done(session: Session, task_id: int) -> Task | None:
    task = session.get(Task, task_id)
    if task:
        task.status = TaskStatus.DONE
        session.add(task)
        session.commit()
        session.refresh(task)
    return task
```

```python
# main.py
from sqlmodel import Session
from database import engine, init_db
from crud import create_task, get_tasks_by_status, mark_done
from models import TaskStatus

if __name__ == "__main__":
    init_db()
    
    with Session(engine) as session:
        # Create tasks
        task1 = create_task(session, "Learn SQLModel", priority=5)
        task2 = create_task(session, "Build project", priority=4)
        
        # Query
        todos = get_tasks_by_status(session, TaskStatus.TODO)
        print(f"TODO tasks: {len(todos)}")
        
        # Update
        mark_done(session, task1.id)
        print(f"Marked task {task1.id} as done")
```

### Checkpoint 3
- [ ] Project has proper file structure
- [ ] Models use enums and validation
- [ ] CRUD is separated into functions
- [ ] Application runs end-to-end

---

## Phase 4: Relationships (Bloom's Level 3-4: Apply & Analyze)

**Goal**: Connect tables with foreign keys and relationships.

### Step 4.1: One-to-Many

```python
from sqlmodel import Field, Relationship, SQLModel

class Author(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    books: list["Book"] = Relationship(back_populates="author")

class Book(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    author_id: int = Field(foreign_key="author.id")
    author: Author = Relationship(back_populates="books")
```

### Step 4.2: Many-to-Many

```python
class StudentCourseLink(SQLModel, table=True):
    student_id: int = Field(foreign_key="student.id", primary_key=True)
    course_id: int = Field(foreign_key="course.id", primary_key=True)

class Student(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    courses: list["Course"] = Relationship(
        back_populates="students", link_model=StudentCourseLink
    )

class Course(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    students: list[Student] = Relationship(
        back_populates="courses", link_model=StudentCourseLink
    )
```

### Checkpoint 4
- [ ] Can implement one-to-many relationships
- [ ] Can implement many-to-many with link table
- [ ] Understand `foreign_key` vs `Relationship`
- [ ] Can navigate relationships in queries

---

## Phase 5: FastAPI Integration (Bloom's Level 4: Analyze)

**Goal**: Build a REST API with SQLModel.

### Complete API Example

```python
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

# Models
class TaskBase(SQLModel):
    title: str
    done: bool = False

class Task(TaskBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class TaskCreate(TaskBase):
    pass

class TaskUpdate(SQLModel):
    title: str | None = None
    done: bool | None = None

# Database
engine = create_engine("sqlite:///api.db", connect_args={"check_same_thread": False})

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

# App
app = FastAPI()

@app.on_event("startup")
def startup():
    SQLModel.metadata.create_all(engine)

@app.post("/tasks/", response_model=Task)
def create_task(task: TaskCreate, session: SessionDep):
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@app.get("/tasks/", response_model=list[Task])
def read_tasks(session: SessionDep, skip: int = 0, limit: int = 100):
    return session.exec(select(Task).offset(skip).limit(limit)).all()

@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: int, session: SessionDep):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: TaskUpdate, session: SessionDep):
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    task_data = task.model_dump(exclude_unset=True)
    db_task.sqlmodel_update(task_data)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: SessionDep):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"deleted": True}
```

Run: `uvicorn main:app --reload`

### Checkpoint 5
- [ ] API has all CRUD endpoints
- [ ] Uses separate models for Create/Update/Response
- [ ] Session injected via dependency
- [ ] Proper error handling with HTTPException

---

## Phase 6: Production Deployment (Bloom's Level 5-6: Evaluate & Create)

**Goal**: Production-ready database application.

### Step 6.1: Add Alembic Migrations

```bash
pip install alembic
alembic init migrations
# Configure env.py and alembic.ini (see migrations.md)
alembic revision --autogenerate -m "Initial"
alembic upgrade head
```

### Step 6.2: Add Testing

```bash
pip install pytest httpx
```

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app, get_session

@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://", poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture
def client(session):
    def override():
        return session
    app.dependency_overrides[get_session] = override
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_create_task(client):
    response = client.post("/tasks/", json={"title": "Test"})
    assert response.status_code == 200
    assert response.json()["title"] == "Test"
```

### Step 6.3: Environment Configuration

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./app.db"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Final Checkpoint
- [ ] Database migrations with Alembic
- [ ] Automated tests passing
- [ ] Environment-based configuration
- [ ] Error handling and validation
- [ ] Documentation (FastAPI auto-docs)

---

## Learning Timeline

| Phase | Duration | Focus |
|-------|----------|-------|
| 1. Hello World | 1-2 hours | Installation, first model |
| 2. Core Concepts | 4-8 hours | CRUD, fields, queries |
| 3. Mini Project | 4-8 hours | Complete application |
| 4. Relationships | 4-8 hours | Foreign keys, joins |
| 5. FastAPI | 4-8 hours | REST API patterns |
| 6. Production | 8-16 hours | Migrations, testing, deployment |

**Total: 25-50 hours** to production proficiency

---

## Next Steps After This Path

1. **Async SQLModel** - For high-concurrency applications
2. **Advanced Queries** - Aggregations, subqueries, CTEs
3. **Database Optimization** - Indexes, query analysis, caching
4. **Multi-tenancy** - Schema-per-tenant patterns
5. **Event Sourcing** - Audit trails, temporal data
