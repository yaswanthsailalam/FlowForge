from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class SupportAccessRequestBase(BaseModel):
    client_id: str
    workspace_id: Optional[str] = None
    reason: str
    scope: str
    duration_hours: int = 4

class SupportAccessRequestCreate(SupportAccessRequestBase):
    pass

class SupportAccessRequestInDB(SupportAccessRequestBase):
    request_id: str
    requested_by: str
    requested_at: datetime
    status: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
