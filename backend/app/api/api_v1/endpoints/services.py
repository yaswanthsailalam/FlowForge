from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from backend.app.api import deps
from backend.app.core.utils import utcnow, new_id, serialize_doc
from backend.app.db.mongodb import db
from backend.app.schemas.service import ServiceCreate, ServiceInDB, ServiceEngagementCreate, ServiceEngagementInDB

router = APIRouter()

services_col = db["service_catalogue"]
engagements_col = db["service_engagements"]

@router.post("/services", response_model=ServiceInDB)
def create_service(
    service_in: ServiceCreate,
    current_user: Any = Depends(deps.require_platform_role(["platform_owner", "platform_service_manager"]))
):
    service = service_in.model_dump()
    service["service_id"] = new_id()
    service["created_at"] = utcnow()
    service["updated_at"] = utcnow()
    services_col.insert_one(service)
    return serialize_doc(service)

@router.get("/services", response_model=List[ServiceInDB])
def list_services(
    current_user: Any = Depends(deps.get_current_user)
):
    return serialize_doc(list(services_col.find({"status": "active"})))

@router.post("/engagements", response_model=ServiceEngagementInDB)
def create_engagement(
    engagement_in: ServiceEngagementCreate,
    current_user: Any = Depends(deps.get_current_user)
):
    engagement = engagement_in.model_dump()
    engagement["engagement_id"] = new_id()
    engagement["created_at"] = utcnow()
    engagement["updated_at"] = utcnow()
    engagements_col.insert_one(engagement)
    return serialize_doc(engagement)

@router.get("/engagements", response_model=List[ServiceEngagementInDB])
def list_engagements(
    client_id: Optional[str] = None,
    current_user: Any = Depends(deps.get_current_user)
):
    query = {}
    if client_id:
        query["client_id"] = client_id
    return serialize_doc(list(engagements_col.find(query)))
