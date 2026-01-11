# Getting Started with FastAPI

## Installation

```bash
# Full installation with all standard dependencies
pip install "fastapi[standard]"

# Minimal installation
pip install fastapi

# With specific ASGI server
pip install fastapi uvicorn
```

## First Application

Create `main.py`:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

## Running the Application

### Development Mode (auto-reload)
```bash
fastapi dev main.py
```
- Runs on http://127.0.0.1:8000
- Auto-reloads on code changes
- Shows detailed errors

### Production Mode
```bash
fastapi run main.py
```

### With Uvicorn directly
```bash
# Development
uvicorn main:app --reload

# Production with workers
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Interactive Documentation

FastAPI automatically generates:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **OpenAPI JSON**: http://127.0.0.1:8000/openapi.json

## App Configuration

```python
app = FastAPI(
    title="My API",
    description="API description with **Markdown** support",
    version="1.0.0",
    docs_url="/docs",           # Swagger UI path (None to disable)
    redoc_url="/redoc",         # ReDoc path (None to disable)
    openapi_url="/openapi.json" # OpenAPI schema path
)
```

## OpenAPI Tags

```python
tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users.",
    },
    {
        "name": "items",
        "description": "Manage items.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://example.com/",
        },
    },
]

app = FastAPI(openapi_tags=tags_metadata)

@app.get("/users/", tags=["users"])
async def read_users():
    return [{"name": "Harry"}]
```

## Requirements File

```
# requirements.txt
fastapi[standard]>=0.100.0
pydantic>=2.0
pydantic-settings>=2.0
sqlmodel>=0.0.14
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.5
httpx>=0.24.0
pytest>=7.0.0
```
