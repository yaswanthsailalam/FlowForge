import pytest
import mongomock
from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import datetime

# Mock MongoDB before importing app components
with patch("pymongo.MongoClient", return_value=mongomock.MongoClient()):
    from backend.app.main import app
    from backend.app.db.mongodb import users_col

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    users_col.delete_many({})

def test_registration_normalization_and_persistence():
    email = "  Test@Example.Com  "
    password = "password123"
    full_name = "Test User"

    # Register
    response = client.post("/api/auth/register", json={
        "email": email,
        "password": password,
        "full_name": full_name
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"

    # Confirm persistence
    user_in_db = users_col.find_one({"email": "test@example.com"})
    assert user_in_db is not None
    assert user_in_db["email"] == "test@example.com"
    assert user_in_db["full_name"] == full_name
    assert "hashed_password" in user_in_db
    assert user_in_db["hashed_password"] != password # Must be hashed

def test_duplicate_registration():
    payload = {"email": "dup@test.com", "password": "p", "full_name": "N"}
    client.post("/api/auth/register", json=payload)
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 409

def test_login_flow():
    email = "login@test.com"
    password = "correct_password"

    # Register
    client.post("/api/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Login User"
    })

    # Login (OAuth2 form format)
    response = client.post("/api/auth/login", data={
        "username": email,
        "password": password
    })
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # Use token for /me
    token = token_data["access_token"]
    me_response = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["email"] == email

def test_login_invalid_credentials():
    client.post("/api/auth/register", json={"email": "wrong@test.com", "password": "p", "full_name": "N"})

    # Wrong password
    res1 = client.post("/api/auth/login", data={"username": "wrong@test.com", "password": "bad"})
    assert res1.status_code == 401

    # Unknown user
    res2 = client.post("/api/auth/login", data={"username": "unknown@test.com", "password": "p"})
    assert res2.status_code == 401
