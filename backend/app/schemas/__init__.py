from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from enum import Enum

class PlatformRole(str, Enum):
    PLATFORM_OWNER = "platform_owner"
    PLATFORM_ADMIN = "platform_admin"
    PLATFORM_PRODUCT_ADMIN = "platform_product_admin"
    PLATFORM_CLIENT_SUCCESS_ADMIN = "platform_client_success_admin"
    PLATFORM_SERVICE_MANAGER = "platform_service_manager"
    PLATFORM_CATALOGUE_ADMIN = "platform_catalogue_admin"
    PLATFORM_REVIEWER = "platform_reviewer"
    PLATFORM_SUPPORT_OPERATOR = "platform_support_operator"
    PLATFORM_SECURITY_AUDITOR = "platform_security_auditor"
    PLATFORM_VIEWER = "platform_viewer"

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    full_name: Optional[str] = None
    is_platform_admin: bool = False
    platform_role: Optional[PlatformRole] = None

# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Additional properties to return via API
class User(UserInDBBase):
    pass

# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None

# Workspace schemas
class WorkspaceBase(BaseModel):
    name: str

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceUpdate(WorkspaceBase):
    status: Optional[str] = None

class WorkspaceInDBBase(WorkspaceBase):
    workspace_id: str
    created_by: str
    status: str = "active"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Workspace(WorkspaceInDBBase):
    pass

# Membership schemas
class WorkspaceMembershipBase(BaseModel):
    role: str

class WorkspaceMembershipCreate(WorkspaceMembershipBase):
    user_id: str
    workspace_id: str

class WorkspaceMembershipInDBBase(WorkspaceMembershipBase):
    membership_id: str
    user_id: str
    workspace_id: str
    status: str = "active"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WorkspaceMembership(WorkspaceMembershipInDBBase):
    pass

class WorkspaceWithRole(Workspace):
    role: str
