# tests/conftest.py
import sys
import os
import types
from types import SimpleNamespace
import pytest
from unittest.mock import MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from bson import ObjectId
import copy

# Simple in-memory mock user storage
_mock_users = {}

def mock_find_one(query=None):
    if not query:
        # Return the first stored user if available
        if _mock_users:
            return copy.deepcopy(next(iter(_mock_users.values())))
        return None
    email = query.get("email")
    return copy.deepcopy(_mock_users.get(email))

def mock_insert_one(user_doc_data):
    if "_id" not in user_doc_data:
        user_doc_data["_id"] = ObjectId()
    _mock_users[user_doc_data["email"]] = copy.deepcopy(user_doc_data)
    return SimpleNamespace(inserted_id=ObjectId(FAKE_USER_ID))


FAKE_USER_ID = "507f1f77bcf86cd799439011"
FAKE_ADMIN_ID = "507f1f77bcf86cd799439012"
FAKE_PRODUCT_ID = "507f1f77bcf86cd799439013"
FAKE_ORDER_ID = "507f1f77bcf86cd799439014"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class MockCursor(list):
    def skip(self, n): return self
    def limit(self, n): return self

fake_db_module = types.ModuleType("configs.database")

product_doc = {
    "_id": ObjectId(FAKE_PRODUCT_ID),
    "name": "T-Shirt",
    "price": 32.4,
    "rating": 4.0,
    "image_url": "https://example.com/tshirt.jpg",
    "category": "Clothing",
    "description": "A comfortable t-shirt",
    "stock": 10
}

try:
    from utils.auth_utils import hash_password
    hashed = hash_password("secret123")
except Exception:
    hashed = "$fake$hash"

user_doc = {
    "_id": ObjectId(FAKE_USER_ID),
    "email": "john@example.com",
    "password": hashed,
    "name": "John Doe",
    "role": "user"
}

order_doc = {
    "_id": ObjectId(FAKE_ORDER_ID),
    "user_id": FAKE_USER_ID,
    "items": [{"product_id": FAKE_PRODUCT_ID, "quantity": 2, "price": product_doc["price"]}],
    "shipping_address": "123 Test Lane",
    "total_amount": product_doc["price"] * 2,
    "status": "Pending"
}

cart_doc = {
    "user_id": FAKE_USER_ID,
    "items": [{"product_id": FAKE_PRODUCT_ID, "quantity": 2}]
}

# ---------------- Mock Collections ----------------
product_collection = MagicMock()
product_collection.find.side_effect = lambda *a, **k: MockCursor([copy.deepcopy(product_doc)])
product_collection.find_one.side_effect = lambda *a, **k: copy.deepcopy(product_doc)
product_collection.insert_one.return_value = SimpleNamespace(acknowledged=True, inserted_id=ObjectId(FAKE_PRODUCT_ID))
product_collection.update_one.return_value = SimpleNamespace(matched_count=1, modified_count=1)
product_collection.delete_one.return_value = SimpleNamespace(deleted_count=1)

user_collection = MagicMock()

user_collection.find_one.side_effect = mock_find_one

user_collection.insert_one.side_effect = mock_insert_one
user_collection.insert_one.return_value = SimpleNamespace(inserted_id=ObjectId(FAKE_USER_ID))
user_collection.count_documents.return_value = 0
user_collection.update_one.return_value = SimpleNamespace(matched_count=1, modified_count=1)
user_collection.delete_one.return_value = SimpleNamespace(deleted_count=1)  # fixed from 0 to 1

cart_collection = MagicMock()
cart_collection.find_one.return_value = copy.deepcopy(cart_doc)
cart_collection.insert_one.return_value = SimpleNamespace(inserted_id=ObjectId())
cart_collection.update_one.return_value = SimpleNamespace(matched_count=1, modified_count=1)  # added matched_count
cart_collection.delete_one.return_value = SimpleNamespace(deleted_count=1)

order_collection = MagicMock()
order_collection.find.side_effect = lambda *a, **k: MockCursor([copy.deepcopy(order_doc)])
order_collection.find_one.side_effect = lambda *a, **k: copy.deepcopy(order_doc)
order_collection.insert_one.return_value = SimpleNamespace(acknowledged=True, inserted_id=ObjectId(FAKE_ORDER_ID))
order_collection.delete_one.return_value = SimpleNamespace(deleted_count=1)

fake_db_module.product_collection = product_collection
fake_db_module.products_collection = product_collection
fake_db_module.user_collection = user_collection
fake_db_module.cart_collection = cart_collection
fake_db_module.order_collection = order_collection

sys.modules["configs.database"] = fake_db_module
sys.modules["database"] = fake_db_module

# ---------------- Auth Dependencies Mock ----------------
fake_auth_dep = types.ModuleType("utils.auth_dependencies")
fake_auth_dep.get_current_user = lambda: {"_id": FAKE_USER_ID, "email": "john@example.com", "role": "user"}
fake_auth_dep.admin_required = lambda: {"_id": FAKE_ADMIN_ID, "email": "admin@example.com", "role": "admin"}

sys.modules["utils.auth_dependencies"] = fake_auth_dep
sys.modules["auth_dependencies"] = fake_auth_dep

# ---------------- App Setup ----------------
from routes import product_routes, cart_routes, order_routes, user_routes, admin_routes

app = FastAPI()
app.include_router(user_routes.router, prefix="/api/v1")
app.include_router(product_routes.router, prefix="/api/v1")
app.include_router(cart_routes.router, prefix="/api/v1")
app.include_router(order_routes.router, prefix="/api/v1")
app.include_router(admin_routes.router, prefix="/api/v1")

client = TestClient(app)

# ---------------- Fixtures ----------------
@pytest.fixture(scope="module")
def normal_user_token():
    return "fake-user-token"

@pytest.fixture(scope="module")
def admin_token():
    return "fake-admin-token"

@pytest.fixture(autouse=True)
def seed_fake_data(tmp_path):
    # Reset in-memory mock users
    _mock_users.clear()

    # Registration toggle
    sys._in_test_register = False

    # Reset mocks before each test
    product_collection.find.side_effect = lambda *a, **k: MockCursor([copy.deepcopy(product_doc)])
    product_collection.find_one.side_effect = lambda *a, **k: copy.deepcopy(product_doc)

    # FIX: use our in-memory mock for find_one
    user_collection.find_one.side_effect = mock_find_one

    cart_collection.find_one.return_value = copy.deepcopy(cart_doc)
    order_collection.find.side_effect = lambda *a, **k: MockCursor([copy.deepcopy(order_doc)])
    order_collection.find_one.side_effect = lambda *a, **k: copy.deepcopy(order_doc)

    # Logging setup
    logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
    os.makedirs(logs_dir, exist_ok=True)
    log_path = os.path.join(logs_dir, "app.log")
    with open(log_path, "w", encoding="utf8") as f:
        f.write("Login successful: user john@example.com\nOrder placed: 1 order created\n")

    yield
    sys._in_test_register = False



@pytest.fixture
def test_user():
    
    from configs import database
    user = {"name": "John Doe", "email": "john@example.com", "password": "secret123"}
    user["password"] = hash_password(user["password"])
    database.user_collection.insert_one(user.copy())  # Insert before test
    yield user
    database.user_collection.delete_many({})  # Cleanup after test