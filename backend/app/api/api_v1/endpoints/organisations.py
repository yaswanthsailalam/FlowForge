from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from backend.app.api import deps
from backend.app.core.utils import utcnow, new_id, serialize_doc
from backend.app.db.mongodb import db
from backend.app.schemas.organisation import ClientOrganisationCreate, ClientOrganisationInDB, ClientOrganisationUpdate

router = APIRouter()

organisations_col = db["client_organisations"]

@router.post("/", response_model=ClientOrganisationInDB)
def create_organisation(
    org_in: ClientOrganisationCreate,
    current_user: Any = Depends(deps.get_current_user)
):
    org_id = new_id()
    now = utcnow()
    org_dict = org_in.model_dump()
    org_dict["organisation_id"] = org_id
    org_dict["created_at"] = now
    org_dict["updated_at"] = now
    org_dict["created_by"] = current_user.user_id
    organisations_col.insert_one(org_dict)
    return serialize_doc(org_dict)

@router.get("/", response_model=List[ClientOrganisationInDB])
def list_organisations(
    current_user: Any = Depends(deps.require_platform_admin)
):
    return serialize_doc(list(organisations_col.find()))

@router.get("/me", response_model=ClientOrganisationInDB)
def get_my_organisation(
    context: dict = Depends(deps.get_workspace_context)
):
    workspace = context["workspace"]
    org_id = workspace.get("organisation_id")
    if not org_id:
        raise HTTPException(status_code=404, detail="Workspace not associated with an organisation")
    org = organisations_col.find_one({"organisation_id": org_id})
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")
    return serialize_doc(org)

@router.patch("/{org_id}", response_model=ClientOrganisationInDB)
def update_organisation(
    org_id: str,
    org_in: ClientOrganisationUpdate,
    current_user: Any = Depends(deps.get_current_user)
):
    org = organisations_col.find_one({"organisation_id": org_id})
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")
    if not current_user.is_platform_admin and org.get("owner_id") != current_user.user_id:
        raise HTTPException(status_code=403, detail="Permission denied")
    update_data = org_in.model_dump(exclude_unset=True)
    update_data["updated_at"] = utcnow()
    organisations_col.update_one({"organisation_id": org_id}, {"$set": update_data})
    return serialize_doc(organisations_col.find_one({"organisation_id": org_id}))
