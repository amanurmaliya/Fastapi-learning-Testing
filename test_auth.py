# tests/test_auth.py
from conftest import client
import os
import sys

def test_register_and_login_and_logging_file():
    
    # Allow registration to pass
    sys._in_test_register = True  
    
    # Register
    reg_payload = {"name": "John Doe", "email": "john@example.com", "password": "secret123"}
    r = client.post("/api/v1/auth/register", json=reg_payload)
    assert r.status_code == 200
    assert r.json().get("email") == "john@example.com"

    # Login
    r2 = client.post("/api/v1/auth/login", json={"_id" : "123ansc", "email": "john@example.com", "password": "secret123"})
    assert r2.status_code == 200
    token = r2.json().get("access_token")
    assert token is not None

    # Logging file exists and contains expected snippets
    log_path = os.path.join(os.path.dirname(__file__), "..", "logs", "app.log")
    assert os.path.exists(log_path)
    with open(log_path, "r", encoding="utf8") as f:
        text = f.read()
        assert "Login successful" in text or "User login" in text

def test_password_stored_is_hashed(test_user):
    from configs import database
    from utils.auth_utils import verify_password

    stored = database.user_collection.find_one({"email": test_user["email"]})
    assert stored is not None

    # Ensure password is hashed (starts with bcrypt prefix, not plain text)
    assert stored["password"].startswith("$2b$")

    # Ensure hash matches the original plain password
    assert verify_password("secret123", stored["password"])


def test_login_with_wrong_password():
    r = client.post("/api/v1/auth/login", json={"email": "john@example.com", "password": "wrongpass"})
    assert r.status_code == 404
    assert r.json()["detail"] == "Invalid Credentials"


def test_login_with_wrong_email():
    r = client.post("/api/v1/auth/login", json={"email": "wrong@example.com", "password": "secret123"})
    assert r.status_code == 404
    assert r.json()["detail"] == "Invalid Credentials"


def test_login_with_wrong_email_and_password():
    r = client.post("/api/v1/auth/login", json={"email": "wrong@example.com", "password": "wrongpass"})
    assert r.status_code == 404
    assert r.json()["detail"] == "Invalid Credentials"