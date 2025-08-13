# tests/test_search.py
from conftest import client

def test_search_product_by_name():
    r = client.post("/api/v1/search-product", json={"query": "T-Shirt"})
    assert r.status_code == 200
    results = r.json()
    assert isinstance(results, list)
    # product name must include query (case-insensitive)
    assert any("t-shirt" in (p["name"].lower()) for p in results)


filter_payload = {
    "category": "Clothing",
    "min_price": 0,
    "max_price": 1000,
    "min_rating": 0
}

def test_filter_products_by_category_and_price_and_rating():
    # Filter by category
    r1 = client.post("/api/v1/filter-products", json=filter_payload)
    assert r1.status_code == 200
    data = r1.json()
    assert isinstance(data, list)
    for product in r1.json():
        assert product.get("category") == "Clothing"

    # Filter by price range
    r2 = client.post("/api/v1/filter-products", json={"min_price": 10, "max_price": 100})
    assert r2.status_code == 200
    for p in r2.json():
        assert 10 <= p.get("price", 0) <= 100

    # Filter by rating
    r3 = client.post("/api/v1/filter-products", json={"min_rating": 4})
    assert r3.status_code == 200
    for p in r3.json():
        assert p.get("rating", 0) >= 4
