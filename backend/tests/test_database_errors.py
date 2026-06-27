import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from pymongo.errors import OperationFailure, ConnectionFailure
from backend.app.main import app
from backend.app.db.mongodb import is_db_connected

client = TestClient(app)

def test_health_check_healthy():
    with patch("backend.app.main.is_db_connected", return_value=True):
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["db"] == "connected"

def test_health_check_unhealthy():
    with patch("backend.app.main.is_db_connected", return_value=False):
        response = client.get("/api/health")
        assert response.status_code == 503
        assert response.json()["detail"]["status"] == "unhealthy"
        assert response.json()["detail"]["db"] == "disconnected"

def test_ready_check_ready():
    with patch("backend.app.main.is_db_connected", return_value=True):
        response = client.get("/api/ready")
        assert response.status_code == 200
        assert response.json()["status"] == "ready"

def test_ready_check_not_ready():
    with patch("backend.app.main.is_db_connected", return_value=False):
        response = client.get("/api/ready")
        assert response.status_code == 503
        assert response.json()["detail"] == "Database not connected"

def test_registration_db_unavailable():
    with patch("backend.app.api.api_v1.endpoints.auth.is_db_connected", return_value=False):
        response = client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "password123", "full_name": "Test User"}
        )
        assert response.status_code == 503
        assert response.json()["detail"] == "DATABASE_UNAVAILABLE"

def test_registration_auth_failure():
    # Mock find_one to raise OperationFailure with "auth failed"
    mock_col = MagicMock()
    mock_col.find_one.side_effect = OperationFailure("auth failed")

    with patch("backend.app.api.api_v1.endpoints.auth.is_db_connected", return_value=True), \
         patch("backend.app.api.api_v1.endpoints.auth.users_col", mock_col):
        response = client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "password123", "full_name": "Test User"}
        )
        assert response.status_code == 503
        assert response.json()["detail"] == "DATABASE_CONFIGURATION_ERROR"

def test_login_db_unavailable():
    with patch("backend.app.api.api_v1.endpoints.auth.is_db_connected", return_value=False):
        response = client.post(
            "/api/auth/login",
            data={"username": "test@example.com", "password": "password123"}
        )
        assert response.status_code == 503
        assert response.json()["detail"] == "DATABASE_UNAVAILABLE"
