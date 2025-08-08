from fastapi.testclient import TestClient
from main import app  # Make sure your FastAPI app is correctly named and imported

client = TestClient(app)

# -------------------------------
# 1. Product Listing - Test Cases
# -------------------------------

def test_product_list_pagination():
    response = client.get("/api/v1/products?page=1&limit=10")
    assert response.status_code == 200
    assert len(response.json()) <= 10

def test_product_display_attributes():
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    for product in response.json():
        assert "name" in product
        assert "image" in product
        assert "price" in product
        assert "rating" in product

def test_product_detail_view():
    response = client.get("/api/v1/products/1")
    assert response.status_code == 200
    product = response.json()
    assert "description" in product
    assert "availability" in product
    assert "related_products" in product

def test_admin_can_add_product():
    new_product = {
        "name": "Test Product",
        "description": "Test Description",
        "price": 100,
        "image_url": "http://example.com/image.jpg",
        "category": "Electronics",
        "rating": 4.5,
        "stock": 10
    }
    response = client.post("/api/v1/admin/products", json=new_product)
    assert response.status_code == 201
    assert response.json()["name"] == "Test Product"

def test_admin_can_update_product():
    update_data = {"price": 150}
    response = client.put("/api/v1/admin/products/1", json=update_data)
    assert response.status_code == 200
    assert response.json()["price"] == 150

def test_admin_can_delete_product():
    response = client.delete("/api/v1/admin/products/1")
    assert response.status_code == 204