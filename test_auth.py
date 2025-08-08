from fastapi.testclient import TestClient
from main import app  # Ensure your FastAPI app is exposed as `app` in main.py

client = TestClient(app)

# ----------------------------
# 1. Authentication & Authorization
# ----------------------------

def test_user_authentication_and_authorization():
    # Register user
    register_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "secret123"
    }
    reg_response = client.post("/api/v1/auth/register", json=register_data)
    assert reg_response.status_code == 201

    # Login
    login_data = {
        "email": "john@example.com",
        "password": "secret123"
    }
    login_response = client.post("/api/v1/auth/login", json=login_data)
    assert login_response.status_code == 200
    token = login_response.json().get("access_token")
    assert token is not None

    # Try to access a protected route
    headers = {"Authorization": f"Bearer {token}"}
    protected_response = client.get("/api/v1/orders", headers=headers)
    assert protected_response.status_code == 200 or protected_response.status_code == 404  # If no orders exist

    # Try accessing without token
    unauthorized_response = client.get("/api/v1/orders")
    assert unauthorized_response.status_code == 401


# ----------------------------
# 2. Password Hashing Test
# ----------------------------

def test_password_is_hashed():
    from database import get_user_by_email  # You must have a user repo/query function
    test_email = "john@example.com"
    user = get_user_by_email(test_email)
    assert user is not None
    assert user.password_hash != "secret123"  # Plain text password should not match
    assert "$" in user.password_hash or user.password_hash.startswith("pbkdf2")  # Example: bcrypt hash


# ----------------------------
# 3. Logging Test (Checkout/Login)
# ----------------------------

def test_logs_created_for_checkout_and_login():
    import os

    log_path = "logs/app.log"  # Assuming this is your log file location
    assert os.path.exists(log_path)

    # Check for login log
    with open(log_path, "r") as log_file:
        logs = log_file.read()
        assert "User login" in logs or "Login successful" in logs

    # Simulate checkout
    client.post("/api/v1/orders", headers={"Authorization": f"Bearer {token}"})
    with open(log_path, "r") as log_file:
        logs = log_file.read()
        assert "Order placed" in logs or "Checkout complete" in logs
