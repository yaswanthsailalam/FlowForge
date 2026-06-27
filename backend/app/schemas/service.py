from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class ServiceBase(BaseModel):
    name: str
    category: str
    description: str
    eligibility: Optional[str] = None
    delivery_model: str
    required_product_ids: List[str] = []
    status: str = "active"
    default_checklist: List[str] = []
    internal_notes: Optional[str] = None

class ServiceCreate(ServiceBase):
    pass

class ServiceInDB(ServiceBase):
    service_id: str
    created_at: datetime
    updated_at: datetime

class ServiceEngagementBase(BaseModel):
    client_id: str
    service_id: str
    request_title: str
    scope_summary: Optional[str] = None
    assigned_team_id: Optional[str] = None
    assigned_owner_id: Optional[str] = None
    client_contact_id: Optional[str] = None
    status: str = "requested"
    milestones: List[Dict[str, Any]] = []
    start_date: Optional[datetime] = None
    target_date: Optional[datetime] = None
    risks: List[str] = []
    blockers: List[str] = []
    acceptance_state: str = "pending"

class ServiceEngagementCreate(ServiceEngagementBase):
    pass

class ServiceEngagementInDB(ServiceEngagementBase):
    engagement_id: str
    created_at: datetime
    updated_at: datetime
    audit_metadata: Dict[str, Any] = {}
