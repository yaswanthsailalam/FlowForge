import pytest
import mongomock
import requests
from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import datetime, timezone

# Mock MongoDB before importing app components
with patch("pymongo.MongoClient", return_value=mongomock.MongoClient()):
    from backend.app.main import app
    from backend.app.db.mongodb import (
        users_col, workspaces_col, workspace_memberships_col,
        workflow_templates_col, workflows_col, workflow_versions_col,
        workflow_runs_col, step_runs_col, tasks_col, approvals_col
    )

client = TestClient(app)

@pytest.fixture
def auth_headers():
    # Register and login a test user
    email = f"test_{datetime.now(timezone.utc).timestamp()}@test.com"
    client.post("/api/auth/register", json={"email": email, "password": "password", "full_name": "Test"})
    login_res = client.post("/api/auth/login", data={"username": email, "password": "password"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def workspace_context(auth_headers):
    # Create a workspace
    ws_res = client.post("/api/workspaces/", json={"name": "Test WS"}, headers=auth_headers)
    ws_id = ws_res.json()["workspace_id"]
    return ws_id, auth_headers

def test_workflow_lifecycle_authenticated(workspace_context):
    workspace_id, headers = workspace_context
    headers["X-Workspace-Id"] = workspace_id

    with patch("backend.app.core.config.settings.ENABLE_POC_ENDPOINTS", True):
        # 1. Seed
        res = client.post("/api/poc/seed", headers=headers)
        assert res.status_code == 200

        # 2. Get templates
        res = client.get("/api/poc/templates", headers=headers)
        assert res.status_code == 200
        templates_res = res.json()
        template_id = templates_res["templates"][0]["template_id"]

        # 3. Create workflow
        wf_res = client.post("/api/poc/workflows", json={
            "template_id": template_id,
            "name": "Test Workflow"
        }, headers=headers)
        assert wf_res.status_code == 200
        workflow_id = wf_res.json()["workflow_id"]

        # 4. Validate
        val_res = client.post(f"/api/poc/workflows/{workflow_id}/validate", headers=headers)
        assert val_res.status_code == 200
        assert val_res.json()["valid"] is True

        # 5. Publish
        pub_res = client.post(f"/api/poc/workflows/{workflow_id}/publish", headers=headers)
        assert pub_res.status_code == 200
        version_id = pub_res.json()["version_id"]

        # 6. Start Run
        run_res = client.post("/api/poc/runs", json={
            "workflow_version_id": version_id,
            "inputs": {"days_requested": "2"}
        }, headers=headers)
        assert run_res.status_code == 200
        run_id = run_res.json()["run_id"]

        # 7. Get Run
        run_data = client.get(f"/api/poc/runs/{run_id}", headers=headers).json()
        assert run_data["run"]["status"] == "waiting_task"
