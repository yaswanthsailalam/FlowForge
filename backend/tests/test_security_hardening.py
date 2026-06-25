import pytest
import mongomock
from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import datetime, timezone

# Mock MongoDB
with patch("pymongo.MongoClient", return_value=mongomock.MongoClient()):
    from backend.app.main import app
    from backend.app.db.mongodb import (
        users_col, workspaces_col, workspace_memberships_col,
        tasks_col, approvals_col
    )
    from backend.app.core.config import settings

client = TestClient(app)

@pytest.fixture
def users():
    """Create two users and return their auth headers."""
    # User A
    email_a = "user_a@test.com"
    client.post("/api/auth/register", json={"email": email_a, "password": "password", "full_name": "User A"})
    login_a = client.post("/api/auth/login", data={"username": email_a, "password": "password"})
    token_a = login_a.json()["access_token"]

    # User B
    email_b = "user_b@test.com"
    client.post("/api/auth/register", json={"email": email_b, "password": "password", "full_name": "User B"})
    login_b = client.post("/api/auth/login", data={"username": email_b, "password": "password"})
    token_b = login_b.json()["access_token"]

    return {
        "a": {"headers": {"Authorization": f"Bearer {token_a}"}, "user_id": users_col.find_one({"email": email_a})["user_id"]},
        "b": {"headers": {"Authorization": f"Bearer {token_b}"}, "user_id": users_col.find_one({"email": email_b})["user_id"]}
    }

@pytest.fixture
def workspaces(users):
    """Create two workspaces and assign memberships."""
    # WS A (User A is Admin)
    ws_a_res = client.post("/api/workspaces/", json={"name": "WS A"}, headers=users["a"]["headers"])
    ws_a_id = ws_a_res.json()["workspace_id"]

    # WS B (User B is Admin)
    ws_b_res = client.post("/api/workspaces/", json={"name": "WS B"}, headers=users["b"]["headers"])
    ws_b_id = ws_b_res.json()["workspace_id"]

    # Also add User A to WS B as an 'operator'
    client.post("/api/workspaces/", json={"name": "dummy"}, headers=users["a"]["headers"]) # just to be sure
    membership_id = "test-membership-id"
    workspace_memberships_col.insert_one({
        "membership_id": membership_id,
        "workspace_id": ws_b_id,
        "user_id": users["a"]["user_id"],
        "role": "operator",
        "status": "active",
        "created_at": datetime.now(timezone.utc)
    })

    return {"a": ws_a_id, "b": ws_b_id}

def test_auth_status_codes(users):
    # 1. Missing token -> 401
    res = client.get("/api/workspaces/")
    assert res.status_code == 401
    assert "WWW-Authenticate" in res.headers

    # 2. Invalid token -> 401
    res = client.get("/api/workspaces/", headers={"Authorization": "Bearer invalid"})
    assert res.status_code == 401

    # 3. Valid token, lack of membership -> 403 (using WS A ID with User B)
    # Note: listing doesn't take X-Workspace-Id, let's use a POC route
    with patch("backend.app.core.config.settings.ENABLE_POC_ENDPOINTS", True):
        res = client.get("/api/poc/templates", headers={**users["b"]["headers"], "X-Workspace-Id": "ws-a-id-doesnt-matter"})
        assert res.status_code == 403
        assert "User is not a member of this workspace" in res.json()["detail"]

def test_cross_workspace_isolation(users, workspaces):
    with patch("backend.app.core.config.settings.ENABLE_POC_ENDPOINTS", True):
        # User A (member of both) but trying to access WS B data using WS A context
        # Setup: Create a task in WS B
        task_id = "task-ws-b"
        tasks_col.insert_one({
            "task_id": task_id,
            "workspace_id": workspaces["b"],
            "status": "pending",
            "run_id": "run-b",
            "step_run_id": "step-b"
        })

        # 1. User A tries to read WS B task using WS A header -> 404 (because query includes workspace_id)
        res = client.post(f"/api/poc/tasks/{task_id}/complete",
                         json={"submitted_data": {}},
                         headers={**users["a"]["headers"], "X-Workspace-Id": workspaces["a"]})
        assert res.status_code == 404

        # 2. User A tries to read WS B task using WS B header (as operator) -> 200 (auth check passes)
        # But wait, we need to make sure User A is permitted for this specific task
        # Let's verify RBAC first.

def test_rbac_and_assignment(users, workspaces):
    with patch("backend.app.core.config.settings.ENABLE_POC_ENDPOINTS", True):
        # Setup: Task in WS B assigned to 'approver' role. User A is 'operator' in WS B.
        task_id = "task-rbac"
        tasks_col.insert_one({
            "task_id": task_id,
            "workspace_id": workspaces["b"],
            "status": "pending",
            "assigned_role": "approver",
            "run_id": "run-b",
            "step_run_id": "step-b"
        })

        # User A (Operator) tries to complete Approver task -> 403
        res = client.post(f"/api/poc/tasks/{task_id}/complete",
                         json={"submitted_data": {}},
                         headers={**users["a"]["headers"], "X-Workspace-Id": workspaces["b"]})
        assert res.status_code == 403

        # User B (Admin) tries to complete Approver task -> 200 (Admin override)
        # Need to mock the run/version lookups to avoid failure later in the endpoint
        with patch("backend.app.db.mongodb.workflow_runs_col.find_one", return_value=None):
            res = client.post(f"/api/poc/tasks/{task_id}/complete",
                             json={"submitted_data": {}},
                             headers={**users["b"]["headers"], "X-Workspace-Id": workspaces["b"]})
            assert res.status_code == 200

def test_poc_guards(users, workspaces):
    # 1. Disabled by default
    res = client.get("/api/poc/templates", headers={**users["a"]["headers"], "X-Workspace-Id": workspaces["a"]})
    assert res.status_code == 404

    # 2. Enabled but no auth -> 401 (deps.get_workspace_context comes after get_current_user)
    with patch("backend.app.core.config.settings.ENABLE_POC_ENDPOINTS", True):
        res = client.get("/api/poc/templates", headers={"X-Workspace-Id": "any"})
        assert res.status_code == 401
