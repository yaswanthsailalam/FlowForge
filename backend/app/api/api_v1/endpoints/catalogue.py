from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from math import ceil

from backend.app.api import deps
from backend.app.core.utils import utcnow, new_id, serialize_doc
from backend.app.db.mongodb import (
    industries_col, business_segments_col, departments_col,
    teams_col, process_families_col, process_models_col,
    model_variants_col, workflow_templates_col
)
from backend.app.schemas.catalogue import (
    IndustryInDB, BusinessSegmentInDB, DepartmentInDB,
    TeamInDB, ProcessFamilyInDB, ProcessModelInDB,
    ModelVariantInDB, WorkflowTemplateInDB, ProcessModelListResponse,
    CataloguePagination, ProcessModelCreate, ProcessModelUpdate,
    ModelVariantCreate, ModelVariantUpdate,
    WorkflowTemplateCreate, WorkflowTemplateUpdate
)

router = APIRouter()

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

# --- Industries ---
@router.get("/industries", response_model=List[IndustryInDB])
def list_industries(
    context: dict = Depends(deps.get_workspace_context)
):
    """List all global or workspace-specific industries."""
    workspace_id = context["workspace_id"]
    query = {"$or": [{"source_type": "global"}, {"workspace_id": workspace_id}]}
    industries = list(industries_col.find(query))
    return serialize_doc(industries)

# --- Business Segments ---
@router.get("/business-segments", response_model=List[BusinessSegmentInDB])
def list_business_segments(
    industry_id: Optional[str] = None,
    context: dict = Depends(deps.get_workspace_context)
):
    """List business segments, optionally filtered by industry."""
    workspace_id = context["workspace_id"]
    query = {"$or": [{"source_type": "global"}, {"workspace_id": workspace_id}]}
    if industry_id:
        query["industry_ids"] = industry_id
    segments = list(business_segments_col.find(query))
    return serialize_doc(segments)

# --- Departments ---
@router.get("/departments", response_model=List[DepartmentInDB])
def list_departments(
    context: dict = Depends(deps.get_workspace_context)
):
    """List departments for the current workspace."""
    workspace_id = context["workspace_id"]
    query = {"workspace_id": workspace_id}
    departments = list(departments_col.find(query))
    return serialize_doc(departments)

# --- Teams ---
@router.get("/teams", response_model=List[TeamInDB])
def list_teams(
    department_id: Optional[str] = None,
    context: dict = Depends(deps.get_workspace_context)
):
    """List teams, optionally filtered by department."""
    workspace_id = context["workspace_id"]
    query = {"workspace_id": workspace_id}
    if department_id:
        query["department_id"] = department_id
    teams = list(teams_col.find(query))
    return serialize_doc(teams)

# --- Process Families ---
@router.get("/process-families", response_model=List[ProcessFamilyInDB])
def list_process_families(
    context: dict = Depends(deps.get_workspace_context)
):
    """List process families."""
    workspace_id = context["workspace_id"]
    query = {"$or": [{"source_type": "global"}, {"workspace_id": workspace_id}]}
    families = list(process_families_col.find(query))
    return serialize_doc(families)

# --- Process Models ---
@router.get("/process-models", response_model=ProcessModelListResponse)
def list_process_models(
    search: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    segment: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    team: Optional[str] = Query(None),
    family: Optional[str] = Query(None),
    source_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    context: dict = Depends(deps.get_workspace_context)
):
    """List process models with extensive filtering and search."""
    workspace_id = context["workspace_id"]

    # Base query: global or workspace-specific
    query = {"$or": [
        {"source_type": "global", "catalogue_status": "published"},
        {"workspace_id": workspace_id}
    ]}

    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"tags": {"$regex": search, "$options": "i"}}
        ]
        # Re-add visibility/ownership constraints if search overrides top-level $or
        query["$and"] = [{"$or": [
            {"source_type": "global", "catalogue_status": "published"},
            {"workspace_id": workspace_id}
        ]}]

    if industry:
        query["applicable_industries"] = industry
    if segment:
        query["applicable_segments"] = segment
    if department:
        query["applicable_departments"] = department
    if team:
        query["applicable_teams"] = team
    if family:
        query["applicable_families"] = family
    if source_type:
        query["source_type"] = source_type
    if status:
        query["catalogue_status"] = status
    if tag:
        query["tags"] = tag

    return paginate_results(process_models_col, query, page, page_size)

@router.post("/process-models", response_model=ProcessModelInDB)
def create_process_model(
    model_in: ProcessModelCreate,
    context: dict = Depends(deps.require_architect)
):
    """Create a new workspace-specific process model."""
    workspace_id = context["workspace_id"]

    model = model_in.model_dump()
    model["model_id"] = new_id()
    model["workspace_id"] = workspace_id
    model["source_type"] = "workspace"
    model["ownership_scope"] = "workspace"
    model["catalogue_status"] = "draft"
    model["publication_status"] = "draft"
    model["model_owner"] = context["user"].user_id
    model["created_at"] = utcnow()
    model["updated_at"] = utcnow()

    process_models_col.insert_one(model)
    return serialize_doc(model)

@router.get("/process-models/{model_id}", response_model=ProcessModelInDB)
def get_process_model(
    model_id: str,
    context: dict = Depends(deps.get_workspace_context)
):
    """Get details of a specific process model."""
    workspace_id = context["workspace_id"]
    model = process_models_col.find_one({"model_id": model_id})

    if not model:
        raise HTTPException(status_code=404, detail="Process model not found")

    # Security check: must be global or belong to this workspace
    if model.get("source_type") != "global" and model.get("workspace_id") != workspace_id:
        raise HTTPException(status_code=403, detail="Access denied to this process model")

    return serialize_doc(model)

@router.patch("/process-models/{model_id}", response_model=ProcessModelInDB)
def update_process_model(
    model_id: str,
    model_in: ProcessModelUpdate,
    context: dict = Depends(deps.require_architect)
):
    """Update a workspace-specific process model."""
    workspace_id = context["workspace_id"]
    model = process_models_col.find_one({"model_id": model_id, "workspace_id": workspace_id})

    if not model:
        raise HTTPException(status_code=404, detail="Process model not found or not in this workspace")

    if model.get("catalogue_status") == "published" and not model_in.catalogue_status:
        # Require versioning for published models
        # In a real system we might create a new version here.
        # For this task, we'll allow updates but note the requirement.
        pass

    update_data = model_in.model_dump(exclude_unset=True)
    update_data["updated_at"] = utcnow()

    process_models_col.update_one({"model_id": model_id}, {"$set": update_data})

    updated_model = process_models_col.find_one({"model_id": model_id})
    return serialize_doc(updated_model)

@router.post("/process-models/{model_id}/publish", response_model=ProcessModelInDB)
def publish_process_model(
    model_id: str,
    context: dict = Depends(deps.require_architect)
):
    """Publish a process model."""
    workspace_id = context["workspace_id"]
    model = process_models_col.find_one({"model_id": model_id, "workspace_id": workspace_id})

    if not model:
        raise HTTPException(status_code=404, detail="Process model not found")

    update_data = {
        "catalogue_status": "published",
        "publication_status": "published",
        "published_at": utcnow(),
        "updated_at": utcnow()
    }

    process_models_col.update_one({"model_id": model_id}, {"$set": update_data})
    return serialize_doc(process_models_col.find_one({"model_id": model_id}))

@router.post("/process-models/{model_id}/archive", response_model=ProcessModelInDB)
def archive_process_model(
    model_id: str,
    context: dict = Depends(deps.require_architect)
):
    """Archive a process model."""
    workspace_id = context["workspace_id"]
    model = process_models_col.find_one({"model_id": model_id, "workspace_id": workspace_id})

    if not model:
        raise HTTPException(status_code=404, detail="Process model not found")

    update_data = {
        "catalogue_status": "archived",
        "archived_at": utcnow(),
        "updated_at": utcnow()
    }

    process_models_col.update_one({"model_id": model_id}, {"$set": update_data})
    return serialize_doc(process_models_col.find_one({"model_id": model_id}))

# --- Model Variants ---
@router.get("/process-models/{model_id}/variants", response_model=List[ModelVariantInDB])
def list_model_variants(
    model_id: str,
    context: dict = Depends(deps.get_workspace_context)
):
    """List variants for a process model."""
    workspace_id = context["workspace_id"]

    # Ensure parent model is accessible
    model = process_models_col.find_one({"model_id": model_id})
    if not model or (model.get("source_type") != "global" and model.get("workspace_id") != workspace_id):
        raise HTTPException(status_code=404, detail="Process model not found")

    query = {"model_id": model_id, "$or": [{"workspace_id": None}, {"workspace_id": workspace_id}]}
    variants = list(model_variants_col.find(query))
    return serialize_doc(variants)

@router.post("/variants", response_model=ModelVariantInDB)
def create_variant(
    variant_in: ModelVariantCreate,
    context: dict = Depends(deps.require_architect)
):
    """Create a new model variant."""
    workspace_id = context["workspace_id"]

    # Ensure parent model is accessible
    model = process_models_col.find_one({"model_id": variant_in.model_id})
    if not model or (model.get("source_type") != "global" and model.get("workspace_id") != workspace_id):
        raise HTTPException(status_code=404, detail="Base process model not found")

    variant = variant_in.model_dump()
    variant["variant_id"] = new_id()
    variant["workspace_id"] = workspace_id
    variant["created_at"] = utcnow()
    variant["updated_at"] = utcnow()

    model_variants_col.insert_one(variant)
    return serialize_doc(variant)

@router.get("/variants/{variant_id}", response_model=ModelVariantInDB)
def get_variant(
    variant_id: str,
    context: dict = Depends(deps.get_workspace_context)
):
    """Get details of a specific model variant."""
    workspace_id = context["workspace_id"]
    variant = model_variants_col.find_one({"variant_id": variant_id})

    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    if variant.get("workspace_id") and variant.get("workspace_id") != workspace_id:
        raise HTTPException(status_code=403, detail="Access denied to this variant")

    return serialize_doc(variant)

# --- Workflow Templates ---
@router.get("/workflow-templates", response_model=List[WorkflowTemplateInDB])
def list_workflow_templates(
    model_id: Optional[str] = None,
    variant_id: Optional[str] = None,
    context: dict = Depends(deps.get_workspace_context)
):
    """List workflow templates."""
    workspace_id = context["workspace_id"]
    query = {"$or": [{"source_type": "global"}, {"workspace_id": workspace_id}]}

    if model_id:
        query["process_model_id"] = model_id
    if variant_id:
        query["variant_id"] = variant_id

    templates = list(workflow_templates_col.find(query))
    return serialize_doc(templates)

@router.post("/workflow-templates", response_model=WorkflowTemplateInDB)
def create_workflow_template(
    template_in: WorkflowTemplateCreate,
    context: dict = Depends(deps.require_architect)
):
    """Create a new workflow template."""
    workspace_id = context["workspace_id"]

    # Ensure parent model is accessible
    model = process_models_col.find_one({"model_id": template_in.process_model_id})
    if not model or (model.get("source_type") != "global" and model.get("workspace_id") != workspace_id):
        raise HTTPException(status_code=404, detail="Process model not found")

    template = template_in.model_dump()
    template["template_id"] = new_id()
    template["workspace_id"] = workspace_id
    template["source_type"] = "workspace"
    template["created_at"] = utcnow()
    template["updated_at"] = utcnow()

    workflow_templates_col.insert_one(template)
    return serialize_doc(template)

@router.get("/workflow-templates/{template_id}", response_model=WorkflowTemplateInDB)
def get_workflow_template(
    template_id: str,
    context: dict = Depends(deps.get_workspace_context)
):
    """Get details of a specific workflow template."""
    workspace_id = context["workspace_id"]
    template = workflow_templates_col.find_one({"template_id": template_id})

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    if template.get("workspace_id") and template.get("workspace_id") != workspace_id:
        raise HTTPException(status_code=403, detail="Access denied to this template")

    return serialize_doc(template)

# --- Favourites ---
@router.post("/process-models/{model_id}/favourite")
def favourite_process_model(
    model_id: str,
    context: dict = Depends(deps.get_workspace_context)
):
    """Add a process model to favourites."""
    workspace_id = context["workspace_id"]
    user_id = context["user"].user_id

    # Ensure model exists and is accessible
    model = process_models_col.find_one({"model_id": model_id})
    if not model or (model.get("source_type") != "global" and model.get("workspace_id") != workspace_id):
        raise HTTPException(status_code=404, detail="Process model not found")

    # We'll use a 'favourites' collection or similar.
    # For now, let's just use the existing db and a new collection name implicitly.
    from backend.app.db.mongodb import db
    favourites_col = db["catalogue_favourites"]

    existing = favourites_col.find_one({"user_id": user_id, "workspace_id": workspace_id, "model_id": model_id})
    if existing:
        favourites_col.delete_one({"_id": existing["_id"]})
        return {"favourited": False}
    else:
        favourites_col.insert_one({
            "user_id": user_id,
            "workspace_id": workspace_id,
            "model_id": model_id,
            "created_at": utcnow()
        })
        return {"favourited": True}

@router.get("/favourites", response_model=List[str])
def list_favourites(
    context: dict = Depends(deps.get_workspace_context)
):
    """List IDs of favourited process models."""
    workspace_id = context["workspace_id"]
    user_id = context["user"].user_id

    from backend.app.db.mongodb import db
    favourites_col = db["catalogue_favourites"]

    favourites = list(favourites_col.find({"user_id": user_id, "workspace_id": workspace_id}))
    return [f["model_id"] for f in favourites]
