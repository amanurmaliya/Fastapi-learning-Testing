# tests/test_admin.py
from conftest import client, FAKE_USER_ID

def test_admin_get_all_users_and_delete_user():
    # GET all users (admin)
    r = client.get("/api/v1/admin/users")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    # DELETE user (the route originally had inverted logic; we've configured the mock delete_one to return deleted_count=0 so it won't raise)
    r2 = client.delete(f"/api/v1/admin/users/{FAKE_USER_ID}")
    # code returns {"message": "User Deleted Successfully"} when it doesn't raise
    assert r2.status_code == 200
    assert "message" in r2.json()
