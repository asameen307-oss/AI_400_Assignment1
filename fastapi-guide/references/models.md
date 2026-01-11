# Pydantic Models and Validation

## Basic Model

```python
from pydantic import BaseModel
from typing import Optional

class Item(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    tax: Optional[float] = None
```

## Model with Validation

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0, description="Price must be positive")
    quantity: int = Field(default=1, ge=1, le=100)
    tags: list[str] = Field(default_factory=list)

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.title()
```

## Nested Models

```python
class Image(BaseModel):
    url: str
    name: str

class Item(BaseModel):
    name: str
    price: float
    images: list[Image] = []

class Offer(BaseModel):
    name: str
    items: list[Item]
```

## Model Inheritance (CRUD Pattern)

```python
from pydantic import BaseModel
from typing import Optional

# Base with shared attributes
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

# For creating (no id)
class ItemCreate(ItemBase):
    pass

# For updating (all optional)
class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

# For reading (includes id)
class ItemResponse(ItemBase):
    id: int

    model_config = {"from_attributes": True}  # For ORM mode
```

## Request Body Examples

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Foo",
                    "price": 35.4
                }
            ]
        }
    }
```

## Field Examples

```python
from pydantic import BaseModel, Field

class Item(BaseModel):
    name: str = Field(examples=["Foo", "Bar"])
    price: float = Field(examples=[35.4, 62.0])
```

## Union Types

```python
from typing import Union

class Cat(BaseModel):
    type: str = "cat"
    meow: str

class Dog(BaseModel):
    type: str = "dog"
    bark: str

@app.post("/animals/")
async def create_animal(animal: Union[Cat, Dog]):
    return animal
```

## Extra Fields Handling

```python
class Item(BaseModel):
    name: str

    model_config = {
        "extra": "forbid"  # Reject extra fields
        # "extra": "ignore"  # Ignore extra fields (default)
        # "extra": "allow"   # Allow extra fields
    }
```

## Custom Serialization

```python
from pydantic import BaseModel, field_serializer
from datetime import datetime

class Event(BaseModel):
    name: str
    timestamp: datetime

    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> str:
        return value.isoformat()
```

## Response Model Filtering

```python
class UserIn(BaseModel):
    username: str
    password: str
    email: str

class UserOut(BaseModel):
    username: str
    email: str

@app.post("/users/", response_model=UserOut)
async def create_user(user: UserIn):
    return user  # password automatically excluded
```

## Generic Models

```python
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    data: T
    message: str
    success: bool = True

@app.get("/items/{item_id}", response_model=Response[Item])
async def read_item(item_id: int):
    return Response(data=items[item_id], message="Success")
```

## Computed Fields

```python
from pydantic import BaseModel, computed_field

class Item(BaseModel):
    price: float
    tax: float = 0.1

    @computed_field
    @property
    def price_with_tax(self) -> float:
        return self.price * (1 + self.tax)
```

## Model Conversion

```python
# Dict to Model
item_data = {"name": "Foo", "price": 35.4}
item = Item(**item_data)
item = Item.model_validate(item_data)

# Model to Dict
item_dict = item.model_dump()
item_dict = item.model_dump(exclude_unset=True)
item_dict = item.model_dump(exclude={"password"})

# JSON
item_json = item.model_dump_json()
item = Item.model_validate_json(json_string)
```
