import pytest
import mongomock
from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import datetime

with patch("pymongo.MongoClient", return_value=mongomock.MongoClient()):
    from backend.app.main import app
    from backend.app.db.mongodb import process_models_col

client = TestClient(app)

def setup_user(email):
    client.post("/api/auth/register", json={"email": email, "password": "password", "full_name": "Test User"})
    login_res = client.post("/api/auth/login", data={"username": email, "password": "password"})
    return login_res.json()["access_token"]

def test_full_governance_lifecycle():
    token = setup_user("architect@test.com")
    ws_res = client.post("/api/workspaces/", json={"name": "Test WS"}, headers={"Authorization": f"Bearer {token}"})
    ws_id = ws_res.json()["workspace_id"]
    headers = {"Authorization": f"Bearer {token}", "X-Workspace-Id": ws_id}

    # 1. Draft -> In Review
    model_res = client.post("/api/catalogue/process-models", json={"name": "Lifecycle Test", "description": "Test"}, headers=headers)
    model_id = model_res.json()["model_id"]

    res = client.post(f"/api/catalogue/process-models/{model_id}/submit-review", json={"comments": "First sub"}, headers=headers)
    assert res.status_code == 200
    assert client.get(f"/api/catalogue/process-models/{model_id}", headers=headers).json()["lifecycle_status"] == "in_review"

    # 2. In Review -> Changes Requested
    res = client.post(f"/api/catalogue/process-models/{model_id}/decision", json={"decision": "changes_requested", "comments": "Fix it"}, headers=headers)
    assert res.status_code == 200
    assert client.get(f"/api/catalogue/process-models/{model_id}", headers=headers).json()["lifecycle_status"] == "changes_requested"

    # 3. Changes Requested -> Draft (via Edit)
    client.patch(f"/api/catalogue/process-models/{model_id}", json={"description": "Updated"}, headers=headers)
    assert client.get(f"/api/catalogue/process-models/{model_id}", headers=headers).json()["lifecycle_status"] == "draft"

    # 4. Resubmit -> In Review -> Approved
    client.post(f"/api/catalogue/process-models/{model_id}/submit-review", json={"comments": "Fixed"}, headers=headers)
    client.post(f"/api/catalogue/process-models/{model_id}/decision", json={"decision": "approved", "comments": "Good"}, headers=headers)
    assert client.get(f"/api/catalogue/process-models/{model_id}", headers=headers).json()["lifecycle_status"] == "approved"

    # 5. Approved -> Published
    res = client.post(f"/api/catalogue/process-models/{model_id}/publish", headers=headers)
    assert res.status_code == 200
    model = client.get(f"/api/catalogue/process-models/{model_id}", headers=headers).json()
    assert model["lifecycle_status"] == "published"
    assert model["is_published"] is True

    # 6. Published -> Immutable
    res = client.patch(f"/api/catalogue/process-models/{model_id}", json={"name": "Break it"}, headers=headers)
    assert res.status_code == 409

    # 7. Published -> Deprecated
    res = client.post(f"/api/catalogue/process-models/{model_id}/deprecate", headers=headers)
    assert res.status_code == 200
    assert client.get(f"/api/catalogue/process-models/{model_id}", headers=headers).json()["lifecycle_status"] == "deprecated"

def test_extension_policy_enforcement():
    token = setup_user("admin@test.com")
    ws_res = client.post("/api/workspaces/", json={"name": "Admin WS"}, headers={"Authorization": f"Bearer {token}"})
    ws_id = ws_res.json()["workspace_id"]
    headers = {"Authorization": f"Bearer {token}", "X-Workspace-Id": ws_id}

    # Create Global Model with Locked mandatory stage
    # (Mocking a global model creation by not providing X-Workspace-Id and being platform admin)
    # Since I don't have a clean bootstrap here, I will just create it in the workspace but use parent/policy logic.

    parent_res = client.post("/api/catalogue/process-models", json={
        "name": "Base Model",
        "description": "Parent",
        "stages": [{"stage_id": "s1", "name": "Mandatory Stage"}],
        "extension_policy": {"locked_mandatory_stages": ["s1"], "allow_additional_stages": False}
    }, headers=headers)
    parent_id = parent_res.json()["model_id"]

    # 1. Reject variant that removes locked stage
    res = client.post("/api/catalogue/process-models", json={
        "name": "Variant Fail",
        "description": "No stages",
        "parent_model_id": parent_id,
        "stages": []
    }, headers=headers)
    assert res.status_code == 400
    assert "Locked mandatory stage" in res.json()["detail"]["violations"][0]

    # 2. Reject variant that adds prohibited stage
    res = client.post("/api/catalogue/process-models", json={
        "name": "Variant Fail 2",
        "description": "Extra stages",
        "parent_model_id": parent_id,
        "stages": [
            {"stage_id": "s1", "name": "Mandatory Stage"},
            {"stage_id": "s2", "name": "Extra"}
        ]
    }, headers=headers)
    assert res.status_code == 400
    assert "Adding new stages" in res.json()["detail"]["violations"][0]

    # 3. Accept valid variant
    res = client.post("/api/catalogue/process-models", json={
        "name": "Valid Variant",
        "description": "Valid",
        "parent_model_id": parent_id,
        "stages": [{"stage_id": "s1", "name": "Mandatory Stage"}]
    }, headers=headers)
    assert res.status_code == 200
