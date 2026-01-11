# Settings and Configuration

## Pydantic Settings (Recommended)

### Installation

```bash
pip install pydantic-settings
```

### Basic Settings

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Awesome API"
    admin_email: str
    items_per_user: int = 50

settings = Settings()
print(settings.app_name)  # From env var APP_NAME or default
```

### Settings with .env File

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_name: str = "My App"
    admin_email: str
    database_url: str
    secret_key: str
    debug: bool = False
```

### Example .env File

```env
APP_NAME="My FastAPI App"
ADMIN_EMAIL=admin@example.com
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-super-secret-key
DEBUG=false
```

### Settings as Dependency

```python
from functools import lru_cache
from typing import Annotated
from fastapi import Depends

@lru_cache
def get_settings():
    return Settings()

@app.get("/info")
async def info(settings: Annotated[Settings, Depends(get_settings)]):
    return {
        "app_name": settings.app_name,
        "admin_email": settings.admin_email
    }
```

### Why @lru_cache

From official docs:
> Creating a Settings object is costly (reads .env file).
> Using @lru_cache ensures settings are read only once.

### Nested Settings

```python
from pydantic import BaseModel
from pydantic_settings import BaseSettings

class DatabaseSettings(BaseModel):
    host: str = "localhost"
    port: int = 5432
    name: str = "app"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__")

    app_name: str = "My App"
    database: DatabaseSettings = DatabaseSettings()
```

```env
DATABASE__HOST=db.example.com
DATABASE__PORT=5432
DATABASE__NAME=production
```

### Environment-Specific Settings

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    database_url: str

    @property
    def is_production(self) -> bool:
        return self.environment == "production"
```

### Validation

```python
from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str

    @field_validator("secret_key")
    @classmethod
    def secret_key_must_be_long(cls, v):
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v
```

### Using Settings in Application

```python
# config.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_name: str = "FastAPI App"
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 30

@lru_cache
def get_settings():
    return Settings()

# main.py
from config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)
```

### Testing with Different Settings

```python
from config import get_settings

def get_settings_override():
    return Settings(
        database_url="sqlite:///:memory:",
        secret_key="test-secret-key-for-testing-only"
    )

app.dependency_overrides[get_settings] = get_settings_override
```

## Middleware Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

class Settings(BaseSettings):
    cors_origins: list[str] = ["http://localhost:3000"]
    cors_allow_credentials: bool = True

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

## Logging Configuration

```python
import logging
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    log_level: str = "INFO"

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
```
