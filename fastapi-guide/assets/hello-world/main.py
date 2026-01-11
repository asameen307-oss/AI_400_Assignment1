"""
FastAPI Hello World - Minimal Example
Run: fastapi dev main.py
Docs: http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI

app = FastAPI(
    title="Hello World API",
    description="A minimal FastAPI application",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Root endpoint returning a greeting."""
    return {"message": "Hello World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    """
    Get an item by ID with optional query parameter.

    - **item_id**: The ID of the item (path parameter)
    - **q**: Optional query string
    """
    return {"item_id": item_id, "q": q}
