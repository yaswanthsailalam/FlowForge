from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from backend.app.api import deps
from backend.app.core.utils import utcnow, new_id, serialize_doc
from backend.app.db.mongodb import db
from backend.app.schemas.support import SupportAccessRequestCreate, SupportAccessRequestInDB
from datetime import timedelta

router = APIRouter()

support_requests_col = db["support_access_requests"]

@router.post("/requests", response_model=SupportAccessRequestInDB)
def request_support_access(
    request_in: SupportAccessRequestCreate,
    current_user: Any = Depends(deps.require_platform_role(["platform_owner", "platform_support_operator"]))
):
    now = utcnow()
    request_dict = request_in.model_dump()
    request_dict["request_id"] = new_id()
    request_dict["requested_by"] = current_user.user_id
    request_dict["requested_at"] = now
    request_dict["status"] = "pending"
    support_requests_col.insert_one(request_dict)
    return serialize_doc(request_dict)

@router.post("/requests/{request_id}/approve", response_model=SupportAccessRequestInDB)
def approve_support_access(
    request_id: str,
    context: dict = Depends(deps.require_admin)
):
    req = support_requests_col.find_one({"request_id": request_id, "status": "pending"})
    if not req:
        raise HTTPException(status_code=404, detail="Pending support request not found")
    if req["workspace_id"] and req["workspace_id"] != context["workspace_id"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    now = utcnow()
    expires_at = now + timedelta(hours=req["duration_hours"])
    support_requests_col.update_one(
        {"request_id": request_id},
        {"$set": {
            "status": "approved",
            "approved_by": context["user"].user_id,
            "approved_at": now,
            "expires_at": expires_at
        }}
    )
    return serialize_doc(support_requests_col.find_one({"request_id": request_id}))

@router.get("/active", response_model=Optional[SupportAccessRequestInDB])
def get_active_support_session(
    context: dict = Depends(deps.get_workspace_context)
):
    now = utcnow()
    req = support_requests_col.find_one({
        "workspace_id": context["workspace_id"],
        "status": "approved",
        "expires_at": {"$gt": now}
    })
    return serialize_doc(req) if req else None
