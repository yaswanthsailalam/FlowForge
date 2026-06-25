from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.core.utils import utcnow, new_id, serialize_doc
from backend.app.db.mongodb import db, workspaces_col, workspace_memberships_col
from backend.app.schemas import Workspace, WorkspaceCreate, User
from backend.app.api import deps

router = APIRouter()

@router.post("/", response_model=Workspace)
def create_workspace(
    *,
    current_user: User = Depends(deps.get_current_user),
    workspace_in: WorkspaceCreate
) -> Any:
    """
    Create a new workspace.
    """
    workspace_id = new_id()
    now = utcnow()

    workspace_dict = {
        "workspace_id": workspace_id,
        "name": workspace_in.name,
        "created_by": current_user.user_id,
        "status": "active",
        "created_at": now,
        "updated_at": now,
    }

    workspaces_col.insert_one(workspace_dict)

    membership_id = new_id()
    membership_dict = {
        "membership_id": membership_id,
        "workspace_id": workspace_id,
        "user_id": current_user.user_id,
        "role": "workspace_admin",
        "status": "active",
        "created_at": now,
        "updated_at": now,
    }
    workspace_memberships_col.insert_one(membership_dict)

    return serialize_doc(workspace_dict)

@router.get("/", response_model=List[Workspace])
def list_workspaces(
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    List workspaces for the current user.
    """
    memberships = list(workspace_memberships_col.find({"user_id": current_user.user_id, "status": "active"}))
    workspace_ids = [m["workspace_id"] for m in memberships]

    workspaces = list(workspaces_col.find({"workspace_id": {"$in": workspace_ids}}))
    return serialize_doc(workspaces)

@router.get("/me", response_model=dict)
def get_active_workspace(
    context: dict = Depends(deps.get_workspace_context)
) -> Any:
    """
    Return the active workspace context.
    """
    return {
        "workspace": serialize_doc(context["workspace"]),
        "role": context["role"]
    }
