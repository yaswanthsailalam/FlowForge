from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from math import ceil

from backend.app.api import deps
from backend.app.core.utils import utcnow, new_id, serialize_doc
from backend.app.db.mongodb import (
    process_models_col, model_variants_col, workflow_templates_col, db
)
from backend.app.schemas.catalogue import (
    ProcessModelCreate, ProcessModelUpdate, ProcessModelInDB,
    ModelReviewSubmit, ModelReviewDecision, ModelReviewInDB,
    ProcessModelListResponse, ModelVariantInDB, WorkflowTemplateInDB
)
from backend.app.core.governance import validate_variant_against_policy, ExtensionPolicyViolation

router = APIRouter()

reviews_col = db["model_reviews"]

# --- Helper for pagination ---
def paginate_results(collection, query, page, page_size):
    total = collection.count_documents(query)
    pages = ceil(total / page_size) if total > 0 else 1
    items = list(collection.find(query).skip((page - 1) * page_size).limit(page_size))

    return {
        "items": serialize_doc(items),
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
            "has_next": page < pages,
            "has_prev": page > 1
        }
    }

@router.get("/process-models", response_model=ProcessModelListResponse)
def list_models(
    search: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    context: dict = Depends(deps.get_workspace_context)
):
    workspace_id = context["workspace_id"]
    query = {"$or": [
        {"source_type": "global", "$or": [{"lifecycle_status": "published"}, {"catalogue_status": "published"}]},
        {"workspace_id": workspace_id}
    ]}

    if search:
        query["$and"] = [{"$or": [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]}]

    if tag:
        query["tags"] = tag

    return paginate_results(process_models_col, query, page, page_size)

@router.post("/process-models", response_model=ProcessModelInDB)
def create_model(
    model_in: ProcessModelCreate,
    context: dict = Depends(deps.get_workspace_context)
):
    user = context["user"]
    workspace_id = context["workspace_id"]
    source_type = "workspace" if workspace_id else "global"

    if source_type == "global" and not user.is_platform_admin:
        raise HTTPException(status_code=403, detail="Only platform admins can create global models")

    if model_in.parent_model_id:
        parent = process_models_col.find_one({"model_id": model_in.parent_model_id})
        if not parent:
            raise HTTPException(status_code=404, detail="Parent model not found")
        try:
            validate_variant_against_policy(parent, model_in.model_dump())
        except ExtensionPolicyViolation as e:
            raise HTTPException(status_code=400, detail={"message": e.message, "violations": e.violations})

    model = model_in.model_dump()
    model["model_id"] = new_id()
    model["source_type"] = source_type
    model["workspace_id"] = workspace_id
    model["lifecycle_status"] = "draft"
    model["catalogue_status"] = "draft"
    model["is_published"] = False
    model["created_at"] = utcnow()
    model["updated_at"] = utcnow()
    model["created_by"] = user.user_id

    process_models_col.insert_one(model)
    return serialize_doc(model)

@router.get("/process-models/{model_id}", response_model=ProcessModelInDB)
def get_model(
    model_id: str,
    context: dict = Depends(deps.get_workspace_context)
):
    model = process_models_col.find_one({"model_id": model_id})
    if not model:
        raise HTTPException(status_code=404, detail="Process model not found")

    if model["source_type"] == "workspace" and model["workspace_id"] != context["workspace_id"]:
        raise HTTPException(status_code=403, detail="Access denied to this workspace model")

    return serialize_doc(model)

@router.patch("/process-models/{model_id}", response_model=ProcessModelInDB)
def update_model(
    model_id: str,
    model_in: ProcessModelUpdate,
    context: dict = Depends(deps.get_workspace_context)
):
    model = process_models_col.find_one({"model_id": model_id})
    if not model:
        raise HTTPException(status_code=404, detail="Process model not found")

    if model.get("is_published"):
        raise HTTPException(status_code=409, detail="Published models are immutable. Please create a new draft version.")

    if model["source_type"] == "global" and not context["user"].is_platform_admin:
        raise HTTPException(status_code=403, detail="Only platform admins can edit global models")
    if model["source_type"] == "workspace" and model["workspace_id"] != context["workspace_id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    if model.get("parent_model_id"):
        parent = process_models_col.find_one({"model_id": model["parent_model_id"]})
        if parent:
            merged_data = model.copy()
            merged_data.update(model_in.model_dump(exclude_unset=True))
            try:
                validate_variant_against_policy(parent, merged_data)
            except ExtensionPolicyViolation as e:
                raise HTTPException(status_code=400, detail={"message": e.message, "violations": e.violations})

    update_data = model_in.model_dump(exclude_unset=True)
    update_data["updated_at"] = utcnow()

    if model["lifecycle_status"] == "changes_requested":
         update_data["lifecycle_status"] = "draft"

    process_models_col.update_one({"model_id": model_id}, {"$set": update_data})
    return serialize_doc(process_models_col.find_one({"model_id": model_id}))

@router.post("/process-models/{model_id}/submit-review", response_model=ModelReviewInDB)
def submit_for_review(
    model_id: str,
    review_in: ModelReviewSubmit,
    context: dict = Depends(deps.get_workspace_context)
):
    model = process_models_col.find_one({"model_id": model_id})
    if not model or model.get("is_published"):
         raise HTTPException(status_code=400, detail="Invalid model for review")

    if model["lifecycle_status"] not in ["draft", "changes_requested"]:
        raise HTTPException(status_code=400, detail=f"Cannot submit model in '{model['lifecycle_status']}' status")

    review = {
        "review_id": new_id(),
        "model_id": model_id,
        "model_version": model["version"],
        "submitted_by": context["user"].user_id,
        "submitted_at": utcnow(),
        "status": "pending",
        "comments": review_in.comments
    }

    reviews_col.insert_one(review)
    process_models_col.update_one({"model_id": model_id}, {"$set": {"lifecycle_status": "in_review"}})

    return serialize_doc(review)

@router.post("/process-models/{model_id}/decision", response_model=ModelReviewInDB)
def decide_review(
    model_id: str,
    decision_in: ModelReviewDecision,
    context: dict = Depends(deps.get_workspace_context)
):
    model = process_models_col.find_one({"model_id": model_id})
    review = reviews_col.find_one({"model_id": model_id, "status": "pending"})

    if not model or not review:
        raise HTTPException(status_code=404, detail="No pending review found for this model")

    if model["source_type"] == "global" and not context["user"].is_platform_admin:
        raise HTTPException(status_code=403, detail="Only platform admins can decide on global reviews")

    status_map = {
        "approved": "approved",
        "changes_requested": "changes_requested",
        "rejected": "archived"
    }

    new_status = status_map.get(decision_in.decision)
    if not new_status:
        raise HTTPException(status_code=400, detail="Invalid decision")

    reviews_col.update_one(
        {"review_id": review["review_id"]},
        {"$set": {
            "status": decision_in.decision,
            "decided_by": context["user"].user_id,
            "decided_at": utcnow(),
            "comments": decision_in.comments
        }}
    )

    process_models_col.update_one({"model_id": model_id}, {"$set": {"lifecycle_status": new_status}})

    return serialize_doc(reviews_col.find_one({"review_id": review["review_id"]}))

@router.post("/process-models/{model_id}/publish", response_model=ProcessModelInDB)
def publish_model(
    model_id: str,
    context: dict = Depends(deps.get_workspace_context)
):
    model = process_models_col.find_one({"model_id": model_id})
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    if model["lifecycle_status"] != "approved":
        raise HTTPException(status_code=400, detail="Model must be approved before publication")

    if model["source_type"] == "global" and not context["user"].is_platform_admin:
        raise HTTPException(status_code=403, detail="Only platform admins can publish global models")

    update_data = {
        "lifecycle_status": "published",
        "catalogue_status": "published",
        "is_published": True,
        "published_at": utcnow(),
        "updated_at": utcnow()
    }

    process_models_col.update_one({"model_id": model_id}, {"$set": update_data})
    return serialize_doc(process_models_col.find_one({"model_id": model_id}))

@router.post("/process-models/{model_id}/deprecate", response_model=ProcessModelInDB)
def deprecate_model(
    model_id: str,
    context: dict = Depends(deps.get_workspace_context)
):
    model = process_models_col.find_one({"model_id": model_id})
    if not model or not model.get("is_published"):
        raise HTTPException(status_code=400, detail="Only published models can be deprecated")

    if model["source_type"] == "global" and not context["user"].is_platform_admin:
        raise HTTPException(status_code=403, detail="Only platform admins can deprecate global models")

    process_models_col.update_one({"model_id": model_id}, {"$set": {"lifecycle_status": "deprecated", "updated_at": utcnow()}})
    return serialize_doc(process_models_col.find_one({"model_id": model_id}))

@router.post("/process-models/{model_id}/archive", response_model=ProcessModelInDB)
def archive_model(
    model_id: str,
    context: dict = Depends(deps.get_workspace_context)
):
    model = process_models_col.find_one({"model_id": model_id})
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    if model["source_type"] == "global" and not context["user"].is_platform_admin:
        raise HTTPException(status_code=403, detail="Only platform admins can archive global models")

    process_models_col.update_one({"model_id": model_id}, {"$set": {"lifecycle_status": "archived", "updated_at": utcnow(), "archived_at": utcnow()}})
    return serialize_doc(process_models_col.find_one({"model_id": model_id}))

@router.post("/process-models/{model_id}/clone", response_model=ProcessModelInDB)
def clone_published_model(
    model_id: str,
    context: dict = Depends(deps.get_workspace_context)
):
    model = process_models_col.find_one({"model_id": model_id})
    if not model or not model.get("is_published"):
        raise HTTPException(status_code=400, detail="Only published models can be cloned for versioning")

    new_model = model.copy()
    new_model.pop("_id")
    new_model["model_id"] = new_id()
    new_model["parent_model_id"] = model_id
    new_model["parent_version"] = model["version"]
    new_model["lifecycle_status"] = "draft"
    new_model["catalogue_status"] = "draft"
    new_model["is_published"] = False
    new_model["created_at"] = utcnow()
    new_model["updated_at"] = utcnow()
    new_model["created_by"] = context["user"].user_id

    v_parts = model["version"].split('.')
    v_parts[-1] = str(int(v_parts[-1]) + 1)
    new_model["version"] = '.'.join(v_parts)

    process_models_col.insert_one(new_model)
    return serialize_doc(new_model)

@router.post("/process-models/{model_id}/favourite")
def favourite_process_model(
    model_id: str,
    context: dict = Depends(deps.get_workspace_context)
):
    workspace_id = context["workspace_id"]
    user_id = context["user"].user_id
    favourites_col = db["catalogue_favourites"]

    existing = favourites_col.find_one({"user_id": user_id, "workspace_id": workspace_id, "model_id": model_id})
    if existing:
        favourites_col.delete_one({"_id": existing["_id"]})
        return {"favourited": False, "model_id": model_id}
    else:
        favourites_col.insert_one({
            "user_id": user_id,
            "workspace_id": workspace_id,
            "model_id": model_id,
            "created_at": utcnow()
        })
        return {"favourited": True, "model_id": model_id}

@router.get("/favourites", response_model=List[str])
def list_favourites(
    context: dict = Depends(deps.get_workspace_context)
):
    workspace_id = context["workspace_id"]
    user_id = context["user"].user_id
    favourites_col = db["catalogue_favourites"]
    favourites = list(favourites_col.find({"user_id": user_id, "workspace_id": workspace_id}))
    return [f["model_id"] for f in favourites]

# --- Related Resources ---

@router.get("/process-models/{model_id}/variants", response_model=List[ModelVariantInDB])
def list_model_variants(
    model_id: str,
    context: dict = Depends(deps.get_workspace_context)
):
    """List organisation variants for a process model."""
    workspace_id = context["workspace_id"]
    # We show variants that belong to the current workspace
    query = {"model_id": model_id, "workspace_id": workspace_id}
    variants = list(model_variants_col.find(query))
    return serialize_doc(variants)

@router.get("/workflow-templates", response_model=List[WorkflowTemplateInDB])
def list_workflow_templates(
    model_id: Optional[str] = Query(None),
    context: dict = Depends(deps.get_workspace_context)
):
    """List workflow templates, optionally filtered by process model."""
    workspace_id = context["workspace_id"]
    # Show global templates OR templates in the current workspace
    query = {"$or": [{"source_type": "global"}, {"workspace_id": workspace_id}]}
    if model_id:
        query["process_model_id"] = model_id

    templates = list(workflow_templates_col.find(query))
    return serialize_doc(templates)
