from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    full_name: Optional[str] = None

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
