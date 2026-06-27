from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class ClientOrganisationBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    industry: Optional[str] = None
    business_segments: List[str] = []
    country: Optional[str] = None
    status: str = "active"
    onboarding_status: str = "pending"
    plan_id: Optional[str] = None
    owner_id: Optional[str] = None

class ClientOrganisationCreate(ClientOrganisationBase):
    pass

class ClientOrganisationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    business_segments: Optional[List[str]] = None
    status: Optional[str] = None
    onboarding_status: Optional[str] = None
    plan_id: Optional[str] = None
    owner_id: Optional[str] = None

class ClientOrganisationInDB(ClientOrganisationBase):
    organisation_id: str
    created_at: datetime
    updated_at: datetime
    created_by: str

class ClientOrganisation(ClientOrganisationInDB):
    pass
