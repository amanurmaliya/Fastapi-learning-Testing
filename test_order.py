# tests/test_order.py
from conftest import client, FAKE_PRODUCT_ID, FAKE_USER_ID

def test_place_order_and_get_detail_and_admin_status_update():
    # Place order (Order model requires products, total, user_id, shipping_address)
    payload = {
        "products": [FAKE_PRODUCT_ID],
        "total": 32.4,
        "user_id": FAKE_USER_ID,
        "shipping_address": "1 Test St"
    }
    r = client.post("/api/v1/orders", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body.get("success") is True
    assert "order_id" in body

    oid = body["order_id"]

    # Get order details
    r2 = client.get(f"/api/v1/orders/{oid}")
    assert r2.status_code == 200
    o = r2.json()
    assert o.get("user_id") is not None
    assert "items" in o
    assert "shipping_address" in o
    assert "total_amount" in o

    # Admin update order status (endpoint expects query param ?status=...)
    r3 = client.put(f"/api/v1/admin/orders/{oid}/status?status=Shipped")
    assert r3.status_code == 200
    assert "Order status updated to Shipped" in r3.json().get("message", "")
