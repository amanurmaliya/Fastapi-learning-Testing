from fastapi.testclient import TestClient
from main import app  # Make sure your FastAPI app is correctly named and imported

client = TestClient(app)

# -----------------------------
# 2. Product Search - Test Cases
# -----------------------------

def test_search_product_by_name():
    response = client.get("/api/v1/search?query=phone")
    assert response.status_code == 200
    for product in response.json():
        assert "phone" in product["name"].lower()

def test_filter_products_by_category():
    response = client.get("/api/v1/products?category=Electronics")
    assert response.status_code == 200
    for product in response.json():
        assert product["category"] == "Electronics"

def test_filter_products_by_price_range():
    response = client.get("/api/v1/products?min_price=100&max_price=500")
    assert response.status_code == 200
    for product in response.json():
        assert 100 <= product["price"] <= 500

def test_filter_products_by_rating():
    response = client.get("/api/v1/products?min_rating=4")
    assert response.status_code == 200
    for product in response.json():
        assert product["rating"] >= 4

def test_search_result_relevance():
    response = client.get("/api/v1/search?query=best+phone")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
