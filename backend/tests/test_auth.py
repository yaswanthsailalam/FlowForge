import pytest
import mongomock
from fastapi.testclient import TestClient
from unittest.mock import patch

# Mock MongoDB before importing app components
with patch("pymongo.MongoClient", return_value=mongomock.MongoClient()):
    from backend.app.main import app
    from backend.app.db.mongodb import users_col, workspaces_col, workspace_memberships_col

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    users_col.delete_many({})
    workspaces_col.delete_many({})
    workspace_memberships_col.delete_many({})

def test_register():
    response = client.post(
        "/api/auth/register",
        json={"email": "user@test.com", "password": "password123", "full_name": "Test User"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "user@test.com"
    assert "hashed_password" not in response.json()

def test_register_duplicate():
    client.post(
        "/api/auth/register",
        json={"email": "user@test.com", "password": "password123", "full_name": "Test User"},
    )
    response = client.post(
        "/api/auth/register",
        json={"email": "user@test.com", "password": "password123", "full_name": "Test User"},
    )
    assert response.status_code == 409

def test_login():
    client.post(
        "/api/auth/register",
        json={"email": "user@test.com", "password": "password123", "full_name": "Test User"},
    )
    response = client.post(
        "/api/auth/login",
        data={"username": "user@test.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_get_me():
    client.post(
        "/api/auth/register",
        json={"email": "user@test.com", "password": "password123", "full_name": "Test User"},
    )
    login_res = client.post(
        "/api/auth/login",
        data={"username": "user@test.com", "password": "password123"},
    )
    token = login_res.json()["access_token"]

    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "user@test.com"

def test_workspace_creation():
    client.post(
        "/api/auth/register",
        json={"email": "user@test.com", "password": "password123", "full_name": "Test User"},
    )
    login_res = client.post(
        "/api/auth/login",
        data={"username": "user@test.com", "password": "password123"},
    )
    token = login_res.json()["access_token"]

    response = client.post(
        "/api/workspaces/",
        json={"name": "Test Workspace"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    workspace_id = response.json()["workspace_id"]

    # Check membership
    membership = workspace_memberships_col.find_one({"workspace_id": workspace_id})
    assert membership is not None
    assert membership["role"] == "workspace_admin"

def test_tenant_isolation():
    # User A
    client.post("/api/auth/register", json={"email": "a@test.com", "password": "password", "full_name": "A"})
    token_a = client.post("/api/auth/login", data={"username": "a@test.com", "password": "password"}).json()["access_token"]
    ws_a_res = client.post("/api/workspaces/", json={"name": "WS A"}, headers={"Authorization": f"Bearer {token_a}"})
    ws_a = ws_a_res.json()["workspace_id"]

    # User B
    client.post("/api/auth/register", json={"email": "b@test.com", "password": "password", "full_name": "B"})
    token_b = client.post("/api/auth/login", data={"username": "b@test.com", "password": "password"}).json()["access_token"]

    # User B tries to access User A's workspace
    response = client.get(
        "/api/workspaces/me",
        headers={"Authorization": f"Bearer {token_b}", "X-Workspace-Id": ws_a}
    )
    assert response.status_code == 403
    assert "not a member" in response.json()["detail"]
