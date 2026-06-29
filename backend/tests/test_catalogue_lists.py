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
        process_models_col, model_variants_col, workflow_templates_col
    )
    from backend.app.core import security

client = TestClient(app)

@pytest.fixture
def auth_context():
    email = "lists@test.com"
    user_id = "u-lists"
    ws_id = "ws-lists"

    users_col.delete_many({})
    users_col.insert_one({
        "user_id": user_id,
        "email": email,
        "hashed_password": security.get_password_hash("password"),
        "full_name": "List Tester",
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })

    workspaces_col.delete_many({})
    workspaces_col.insert_one({
        "workspace_id": ws_id,
        "name": "Test Workspace",
        "created_by": user_id,
        "status": "active",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })

    workspace_memberships_col.delete_many({})
    workspace_memberships_col.insert_one({
        "workspace_id": ws_id,
        "user_id": user_id,
        "role": "workspace_admin",
        "status": "active",
        "created_at": datetime.utcnow()
    })

    token = security.create_access_token(user_id)
    return {
        "headers": {
            "Authorization": f"Bearer {token}",
            "X-Workspace-Id": ws_id
        },
        "workspace_id": ws_id
    }

def test_variants_list_endpoint(auth_context):
    model_id = "m1"
    headers = auth_context["headers"]
    ws_id = auth_context["workspace_id"]

    model_variants_col.delete_many({})
    model_variants_col.insert_one({
        "variant_id": "v1",
        "model_id": model_id,
        "workspace_id": ws_id,
        "name": "V1",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })

    res = client.get(f"/api/catalogue/process-models/{model_id}/variants", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["variant_id"] == "v1"

def test_templates_list_endpoint(auth_context):
    model_id = "m1"
    headers = auth_context["headers"]
    ws_id = auth_context["workspace_id"]

    workflow_templates_col.delete_many({})
    workflow_templates_col.insert_one({
        "template_id": "t1",
        "process_model_id": model_id,
        "workspace_id": ws_id,
        "name": "T1",
        "source_type": "workspace",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })

    res = client.get(f"/api/catalogue/workflow-templates?model_id={model_id}", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["template_id"] == "t1"
