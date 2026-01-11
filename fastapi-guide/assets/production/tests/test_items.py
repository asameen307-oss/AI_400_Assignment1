"""Tests for items endpoints."""
from fastapi.testclient import TestClient


def test_create_item(client: TestClient):
    """Test creating an item."""
    response = client.post(
        "/items/",
        json={"name": "Test Item", "description": "A test item", "price": 10.99},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["price"] == 10.99
    assert "id" in data


def test_read_items(client: TestClient):
    """Test reading all items."""
    # Create an item first
    client.post("/items/", json={"name": "Item 1", "price": 5.0})

    response = client.get("/items/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_read_item(client: TestClient):
    """Test reading a single item."""
    # Create an item first
    create_response = client.post("/items/", json={"name": "Item", "price": 5.0})
    item_id = create_response.json()["id"]

    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Item"


def test_read_item_not_found(client: TestClient):
    """Test reading non-existent item."""
    response = client.get("/items/999")
    assert response.status_code == 404


def test_update_item(client: TestClient):
    """Test updating an item."""
    # Create an item first
    create_response = client.post("/items/", json={"name": "Old Name", "price": 5.0})
    item_id = create_response.json()["id"]

    response = client.patch(f"/items/{item_id}", json={"name": "New Name"})
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


def test_delete_item(client: TestClient):
    """Test deleting an item."""
    # Create an item first
    create_response = client.post("/items/", json={"name": "To Delete", "price": 5.0})
    item_id = create_response.json()["id"]

    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 200

    # Verify deleted
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 404
