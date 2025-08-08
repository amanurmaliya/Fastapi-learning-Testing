from fastapi.testclient import TestClient
from main import app  # Make sure your FastAPI app is correctly named and imported

client = TestClient(app)


# 3. Cart Management - Test Cases
# -----------------------------

def test_add_product_to_cart():
    response = client.post("/api/v1/cart", json={"product_id": 1, "quantity": 2})
    assert response.status_code == 200
    assert response.json()["message"] == "Product added to cart"

def test_remove_product_from_cart():
    response = client.delete("/api/v1/cart/1")
    assert response.status_code == 200
    assert response.json()["message"] == "Product removed from cart"

def test_update_cart_item_quantity():
    response = client.put("/api/v1/cart", json={"product_id": 1, "quantity": 5})
    assert response.status_code == 200
    assert response.json()["message"] == "Cart updated"

def test_cart_total_calculation():
    response = client.get("/api/v1/cart")
    assert response.status_code == 200
    cart = response.json()
    total = sum(item["quantity"] * item["price"] for item in cart["items"])
    assert cart["total_price"] == total