# tests/test_cart.py
from conftest import client, FAKE_PRODUCT_ID, FAKE_USER_ID

def test_add_product_to_cart():
    r = client.post(f"/api/v1/cart/{FAKE_USER_ID}/add", json={"product_id": FAKE_PRODUCT_ID, "quantity": 2})
    assert r.status_code == 200
    assert r.json().get("message") == "Product added to Cart"

def test_update_cart_item_quantity():
    # This will get save the data for the current 
    client.post(f"/api/v1/cart/{FAKE_USER_ID}/add", json={"product_id": FAKE_PRODUCT_ID, "quantity": 2})
    
    # This will update it
    r = client.put(f"/api/v1/cart/{FAKE_USER_ID}/update", json={
        "product_id": FAKE_PRODUCT_ID,
        "quantity": 5
    })
    assert r.status_code == 200
    assert r.json().get("message") == "Quantity Updated"

def test_cart_total_and_items_present():
    r = client.get(f"/api/v1/cart/{FAKE_USER_ID}")
    assert r.status_code == 200
    body = r.json()
    assert "items" in body
    assert "total_price" in body
    assert isinstance(body["items"], list)
