from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class ApplicationBase(BaseModel):
    name: str
    vendor: Optional[str] = None
    category: str
    application_type: str
    supported_integration_methods: List[str] = []
    status: str = "active"
    documentation_url: Optional[str] = None
    supported_environments: List[str] = ["production", "staging", "development"]

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationInDB(ApplicationBase):
    app_id: str
    created_at: datetime
    updated_at: datetime

class ClientAppInstanceBase(BaseModel):
    client_id: str
    app_catalogue_id: str
    display_name: str
    environment_type: str
    business_owner_id: Optional[str] = None
    technical_owner_id: Optional[str] = None
    status: str = "not_configured"
    data_classification: str = "internal"
    workspace_ids: List[str] = []

class ClientAppInstanceCreate(ClientAppInstanceBase):
    pass

class ClientAppInstanceInDB(ClientAppInstanceBase):
    instance_id: str
    created_at: datetime
    updated_at: datetime
    last_check_at: Optional[datetime] = None
    connection_status_details: Optional[str] = None
