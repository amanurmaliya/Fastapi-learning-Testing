from fastapi.testclient import TestClient
from main import app  # Make sure your FastAPI app is correctly named and imported

client = TestClient(app)

# -----------------------------
# 4. Order Management - Test Cases
# -----------------------------

def test_place_order_from_cart():
    response = client.post("/api/v1/orders")
    assert response.status_code == 201
    assert "order_id" in response.json()

def test_order_has_valid_status_flow():
    statuses = ["Pending", "Confirmed", "Shipped", "Delivered", "Cancelled"]
    for status in statuses:
        response = client.put("/api/v1/admin/orders/1/status", json={"status": status})
        assert response.status_code == 200
        assert response.json()["status"] == status

def test_user_can_view_order_history():
    response = client.get("/api/v1/orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_admin_can_update_order_status():
    response = client.put("/api/v1/admin/orders/1/status", json={"status": "Shipped"})
    assert response.status_code == 200
    assert response.json()["status"] == "Shipped"

def test_order_details_are_captured_correctly():
    response = client.get("/api/v1/orders/1")
    assert response.status_code == 200
    order = response.json()
    assert "user_id" in order
    assert "items" in order
    assert "shipping_address" in order
    assert "total_amount" in order
    assert "status" in order