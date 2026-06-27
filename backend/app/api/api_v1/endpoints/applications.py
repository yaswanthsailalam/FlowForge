from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from backend.app.api import deps
from backend.app.core.utils import utcnow, new_id, serialize_doc
from backend.app.db.mongodb import db
from backend.app.schemas.application import ApplicationCreate, ApplicationInDB, ClientAppInstanceCreate, ClientAppInstanceInDB

router = APIRouter()

app_catalogue_col = db["application_catalogue"]
app_instances_col = db["client_app_instances"]

@router.post("/catalogue", response_model=ApplicationInDB)
def create_catalogue_app(
    app_in: ApplicationCreate,
    current_user: Any = Depends(deps.require_platform_role(["platform_owner", "platform_product_admin"]))
):
    app = app_in.model_dump()
    app["app_id"] = new_id()
    app["created_at"] = utcnow()
    app["updated_at"] = utcnow()
    app_catalogue_col.insert_one(app)
    return serialize_doc(app)

@router.get("/catalogue", response_model=List[ApplicationInDB])
def list_catalogue_apps(
    current_user: Any = Depends(deps.get_current_user)
):
    return serialize_doc(list(app_catalogue_col.find({"status": "active"})))

@router.post("/instances", response_model=ClientAppInstanceInDB)
def register_app_instance(
    instance_in: ClientAppInstanceCreate,
    current_user: Any = Depends(deps.get_current_user)
):
    instance = instance_in.model_dump()
    instance["instance_id"] = new_id()
    instance["created_at"] = utcnow()
    instance["updated_at"] = utcnow()
    app_instances_col.insert_one(instance)
    return serialize_doc(instance)

@router.get("/instances", response_model=List[ClientAppInstanceInDB])
def list_app_instances(
    client_id: Optional[str] = None,
    current_user: Any = Depends(deps.get_current_user)
):
    query = {}
    if client_id:
        query["client_id"] = client_id
    return serialize_doc(list(app_instances_col.find(query)))
