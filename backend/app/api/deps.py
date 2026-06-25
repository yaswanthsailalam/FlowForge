from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError

from backend.app.core import security
from backend.app.core.config import settings
from backend.app.core.utils import serialize_doc
from backend.app.db.mongodb import users_col, workspaces_col, workspace_memberships_col
from backend.app.schemas import TokenPayload, User, WorkspaceMembership

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_current_user(
    token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = users_col.find_one({"user_id": token_data.sub})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.get("is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return User(**serialize_doc(user))

def get_workspace_context(
    current_user: User = Depends(get_current_user),
    x_workspace_id: str = Header(..., description="The ID of the workspace to operate in")
) -> dict:
    """
    FastAPI dependency to establish the workspace context.
    Returns a dict containing user, workspace, and membership info.
    """
    membership = workspace_memberships_col.find_one({
        "workspace_id": x_workspace_id,
        "user_id": current_user.user_id,
        "status": "active"
    })

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a member of this workspace"
        )

    workspace = workspaces_col.find_one({"workspace_id": x_workspace_id})
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return {
        "user": current_user,
        "workspace_id": x_workspace_id,
        "workspace": workspace,
        "membership": membership,
        "role": membership["role"]
    }

def check_permissions(required_roles: list):
    def role_checker(context: dict = Depends(get_workspace_context)):
        if context["role"] not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{context['role']}' lacks required permissions"
            )
        return context
    return role_checker

# Role-specific shortcuts
require_admin = check_permissions(["workspace_admin"])
require_architect = check_permissions(["workspace_admin", "process_architect"])
require_manager = check_permissions(["workspace_admin", "department_manager"])
require_operator = check_permissions(["workspace_admin", "operator"])
require_approver = check_permissions(["workspace_admin", "approver"])

def require_poc_enabled():
    if not settings.ENABLE_POC_ENDPOINTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="POC endpoints are not enabled in this environment"
        )
