import pytest
import mongomock
from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import datetime

# Mock MongoDB before importing app components
with patch("pymongo.MongoClient", return_value=mongomock.MongoClient()):
    from backend.app.main import app
    from backend.app.db.mongodb import (
        users_col, workspaces_col, workspace_memberships_col,
        process_models_col, workflows_col
    )
    from backend.app.core.config import settings

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    users_col.delete_many({})
    workspaces_col.delete_many({})
    workspace_memberships_col.delete_many({})
    process_models_col.delete_many({})
    workflows_col.delete_many({})

def setup_user_and_workspace(email, ws_name):
    client.post("/api/auth/register", json={"email": email, "password": "password", "full_name": "Test User"})
    login_res = client.post("/api/auth/login", data={"username": email, "password": "password"})
    token = login_res.json()["access_token"]
    ws_res = client.post("/api/workspaces/", json={"name": ws_name}, headers={"Authorization": f"Bearer {token}"})
    workspace_id = ws_res.json()["workspace_id"]
    return token, workspace_id

def test_create_blank_draft():
    token, ws_id = setup_user_and_workspace("admin@test.com", "Test WS")
    headers = {"Authorization": f"Bearer {token}", "X-Workspace-Id": ws_id}

    payload = {"name": "Test Blank", "description": "Test Desc", "source_type": "blank"}
    response = client.post("/api/workflows/draft/blank", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Blank"
    assert data["source_type"] == "blank"
    assert data["status"] == "draft"

def test_list_drafts():
    token, ws_id = setup_user_and_workspace("admin@test.com", "Test WS")
    headers = {"Authorization": f"Bearer {token}", "X-Workspace-Id": ws_id}

    client.post("/api/workflows/draft/blank", json={"name": "Draft 1", "source_type": "blank"}, headers=headers)
    client.post("/api/workflows/draft/blank", json={"name": "Draft 2", "source_type": "blank"}, headers=headers)

    response = client.get("/api/workflows/drafts", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_update_draft():
    token, ws_id = setup_user_and_workspace("admin@test.com", "Test WS")
    headers = {"Authorization": f"Bearer {token}", "X-Workspace-Id": ws_id}

    create_res = client.post("/api/workflows/draft/blank", json={"name": "Old Name", "source_type": "blank"}, headers=headers)
    workflow_id = create_res.json()["workflow_id"]

    update_payload = {"name": "New Name", "definition": {"trigger": {"type": "scheduled", "name": "Daily"}}}
    response = client.patch(f"/api/workflows/drafts/{workflow_id}", json=update_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["definition"]["trigger"]["type"] == "scheduled"

def test_validate_draft():
    token, ws_id = setup_user_and_workspace("admin@test.com", "Test WS")
    headers = {"Authorization": f"Bearer {token}", "X-Workspace-Id": ws_id}

    # Create invalid draft (no steps)
    create_res = client.post("/api/workflows/draft/blank", json={"name": "Invalid Draft", "source_type": "blank"}, headers=headers)
    workflow_id = create_res.json()["workflow_id"]

    response = client.post(f"/api/workflows/drafts/{workflow_id}/validate", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["validation_status"] == "invalid"
    assert any(i["category"] == "steps" for i in data["issues"])

def test_tenant_isolation():
    token_a, ws_a = setup_user_and_workspace("a@test.com", "WS A")
    token_b, ws_b = setup_user_and_workspace("b@test.com", "WS B")

    headers_a = {"Authorization": f"Bearer {token_a}", "X-Workspace-Id": ws_a}
    headers_b = {"Authorization": f"Bearer {token_b}", "X-Workspace-Id": ws_b}

    # Create draft in workspace A
    create_res = client.post("/api/workflows/draft/blank", json={"name": "WS1 Draft", "source_type": "blank"}, headers=headers_a)
    workflow_id = create_res.json()["workflow_id"]

    # Try to access from workspace B
    response = client.get(f"/api/workflows/drafts/{workflow_id}", headers=headers_b)
    assert response.status_code == 404
