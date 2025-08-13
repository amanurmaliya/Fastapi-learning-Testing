# tests/test_product.py
from conftest import client, FAKE_PRODUCT_ID, FAKE_USER_ID  # conftest lives in the same folder for pytest discovery
import json

def test_product_list_pagination():
    """
    Calls:   GET /api/v1/product-list?page=1&limit=10
    Asserts: 200 and <= 10 items
    """
    r = client.get("/api/v1/product-list?page=1&limit=10")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) <= 10

def test_product_display_attributes():
    """
    Calls:   GET /api/v1/product-list
    Asserts: each product has expected keys
    """
    r = client.get("/api/v1/product-list")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1
    for p in items:
        # product model uses `image_url` (consistent with product_models.py).
        assert "name" in p
        assert "price" in p
        assert "rating" in p
        assert "image_url" in p

def test_product_detail_view_and_update_and_delete_and_add():
    """
    Full small flow using product id returned from product-list:
    - GET detail
    - POST update (product_routes uses POST for update)
    - DELETE product
    - POST add product
    """
    # 1) get product list and pick an id
    r = client.get("/api/v1/product-list")
    assert r.status_code == 200
    pid = r.json()[0]["id"]

    # 2) detail
    r2 = client.get(f"/api/v1/product/{pid}")
    assert r2.status_code == 200
    p = r2.json()
    assert "description" in p
    assert "id" in p

    # 3) update (product_routes uses POST /product/{id} for update)
    update_payload = {**p, "price": 99.99}
    # update_payload["_id"] = str(pid["_id"])  # Ensure serializable
    
    r3 = client.post(f"/api/v1/product/{pid}", json=update_payload)
    assert r3.status_code == 200
    assert r3.json().get("message") == "Product updated successfully"

    # 4) delete
    r4 = client.delete(f"/api/v1/product/{pid}")
    assert r4.status_code == 200
    assert "Product Deleted Successfully" in r4.json().get("message", "")

    # 5) add new product (admin-only in code; our fake admin dependency allows it)
    new_prod = {
        "_id": "507f1f77bcf86cd799439015",
        "name": "Test Product",
        "price": 100,
        "description": "Test",
        "stock": 5,
        "image_url": "http://example.com/x.jpg",
        "category": "Test",
        "rating": 4.2
    }
    r5 = client.post("/api/v1/add-product", json=new_prod)
    assert r5.status_code == 200
    assert r5.json().get("success") is True
