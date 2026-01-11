# SQLModel Database Migrations with Alembic

Alembic handles database schema changes (migrations) for SQLModel projects.

## Installation

```bash
pip install alembic
```

## Initial Setup

### 1. Initialize Alembic

```bash
alembic init migrations
```

Creates:
```
migrations/
├── versions/          # Migration scripts go here
├── env.py             # Migration environment config
├── README
└── script.py.mako     # Template for new migrations
alembic.ini            # Main config file
```

### 2. Configure `alembic.ini`

```ini
# alembic.ini
[alembic]
script_location = migrations
sqlalchemy.url = sqlite:///./database.db

# For PostgreSQL:
# sqlalchemy.url = postgresql://user:password@localhost:5432/dbname
```

### 3. Configure `env.py`

```python
# migrations/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import SQLModel and your models
from sqlmodel import SQLModel

# IMPORTANT: Import all your models here
from app.models import Hero, Team  # Your models

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata to SQLModel's metadata
target_metadata = SQLModel.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # Required for SQLite
        user_module_prefix="sqlmodel.sql.sqltypes.",
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # Required for SQLite
            user_module_prefix="sqlmodel.sql.sqltypes.",
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 4. Update `script.py.mako`

Add SQLModel import to migration template:

```mako
# migrations/script.py.mako
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel  # ADD THIS LINE
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
```

---

## Common Commands

### Generate Migration (Auto-detect changes)

```bash
alembic revision --autogenerate -m "Add hero table"
```

### Apply Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade <revision_id>

# Apply next migration
alembic upgrade +1
```

### Rollback Migrations

```bash
# Rollback one step
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback all
alembic downgrade base
```

### View Status

```bash
# Current revision
alembic current

# Migration history
alembic history

# Show SQL without applying
alembic upgrade head --sql
```

---

## Migration Workflow

### Adding a New Column

1. **Update model:**
```python
class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: int | None = None
    power_level: int = Field(default=0)  # New column
```

2. **Generate migration:**
```bash
alembic revision --autogenerate -m "Add power_level to hero"
```

3. **Review generated migration:**
```python
# migrations/versions/xxxx_add_power_level_to_hero.py
def upgrade() -> None:
    op.add_column('hero', sa.Column('power_level', sa.Integer(), nullable=False))

def downgrade() -> None:
    op.drop_column('hero', 'power_level')
```

4. **Apply:**
```bash
alembic upgrade head
```

### Creating a New Table

1. **Create model:**
```python
class Villain(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    evil_plan: str
```

2. **Generate and apply:**
```bash
alembic revision --autogenerate -m "Add villain table"
alembic upgrade head
```

---

## Existing Database Setup

When adding Alembic to a project with an existing database:

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Mark as applied without running (database already has tables)
alembic stamp head
```

---

## Environment Variables for Database URL

```python
# migrations/env.py
import os

def run_migrations_online() -> None:
    # Get URL from environment, fallback to config file
    url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    
    connectable = create_engine(url)
    # ... rest of function
```

---

## Production Deployment

### CI/CD Pipeline

```yaml
# Example GitHub Actions
- name: Run migrations
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
  run: |
    alembic upgrade head
```

### Docker Entrypoint

```bash
#!/bin/bash
# entrypoint.sh
alembic upgrade head
exec "$@"
```

### Pre-deploy Check

```bash
# Check for pending migrations
alembic check
# Returns error if migrations needed
```

---

## Common Issues

### SQLite Batch Mode

SQLite doesn't support many ALTER operations. Use `render_as_batch=True`:

```python
context.configure(
    connection=connection,
    target_metadata=target_metadata,
    render_as_batch=True,  # Required for SQLite
)
```

### Models Not Detected

Ensure all models are imported in `env.py` before setting `target_metadata`:

```python
# Import all models BEFORE this line
from app.models import Hero, Team, Villain

target_metadata = SQLModel.metadata
```

### SQLModel Type Issues

Add `user_module_prefix` for SQLModel custom types:

```python
context.configure(
    connection=connection,
    target_metadata=target_metadata,
    user_module_prefix="sqlmodel.sql.sqltypes.",
)
```

---

## Project Structure Example

```
myproject/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py        # SQLModel models
│   └── database.py      # Engine, session setup
├── migrations/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── alembic.ini
└── requirements.txt
```

```python
# app/models.py
from sqlmodel import Field, SQLModel

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    secret_name: str

# app/database.py  
from sqlmodel import create_engine

DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL)
```

```python
# migrations/env.py
import sys
sys.path.insert(0, '.')  # Add project root to path

from sqlmodel import SQLModel
from app.models import *  # Import all models

target_metadata = SQLModel.metadata
```
