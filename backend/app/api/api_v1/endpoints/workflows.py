from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.api import deps
from backend.app.core.utils import utcnow, new_id, serialize_doc
from backend.app.db.mongodb import (
    workflows_col, process_models_col, model_variants_col,
    workflow_templates_col
)
from backend.app.schemas.workflow import (
    WorkflowDraftInDB, WorkflowDraftCreate, WorkflowDraftUpdate,
    WorkflowDraftList, WorkflowDefinition, TriggerDefinition
)
from backend.app.core.engine import create_audit_event

router = APIRouter()

def get_base_draft(name: str, description: str, source_type: str, workspace_id: str, user_id: str) -> dict:
    return {
        "workflow_id": new_id(),
        "workspace_id": workspace_id,
        "name": name,
        "description": description,
        "status": "draft",
        "source_type": source_type,
        "configuration_complete": False,
        "validation_status": "not_validated",
        "validation_results": [],
        "unresolved_configuration": [],
        "created_by": user_id,
        "updated_by": user_id,
        "created_at": utcnow(),
        "updated_at": utcnow(),
        "version": 1,
        "definition": {
            "trigger": {
                "trigger_id": "trigger-1",
                "type": "manual",
                "name": "Manual Trigger",
                "description": "Manually start this workflow",
                "config": {},
                "input_schema": {}
            },
            "inputs": [],
            "documents": [],
            "stages": [],
            "steps": [],
            "participants": [],
            "approvals": [],
            "notifications": [],
            "completion": {
                "valid_states": ["completed"],
                "required_outputs": [],
                "cancellation_behaviour": "cancel_pending",
                "incomplete_data_behaviour": "allow_completion"
            }
        }
    }

@router.post("/draft/blank", response_model=WorkflowDraftInDB)
def create_blank_draft(
    draft_in: WorkflowDraftCreate,
    context: dict = Depends(deps.require_architect)
):
    """Create a blank workflow draft."""
    workspace_id = context["workspace_id"]
    user_id = context["user"].user_id

    draft = get_base_draft(
        name=draft_in.name,
        description=draft_in.description,
        source_type="blank",
        workspace_id=workspace_id,
        user_id=user_id
    )

    workflows_col.insert_one(draft)

    create_audit_event(
        workspace_id=workspace_id,
        actor_id=user_id,
        actor_role=context["role"],
        event_type="workflow_draft_created",
        entity_type="workflow",
        entity_id=draft["workflow_id"],
        metadata={"source_type": "blank"}
    )

    return serialize_doc(draft)

@router.post("/draft/from-model/{model_id}", response_model=WorkflowDraftInDB)
def create_draft_from_model(
    model_id: str,
    draft_in: WorkflowDraftCreate,
    context: dict = Depends(deps.require_architect)
):
    """Create a workflow draft from a process model."""
    workspace_id = context["workspace_id"]
    user_id = context["user"].user_id

    model = process_models_col.find_one({"model_id": model_id})
    if not model:
        raise HTTPException(status_code=404, detail="Process model not found")

    if model.get("source_type") != "global" and model.get("workspace_id") != workspace_id:
        raise HTTPException(status_code=403, detail="Access denied to this process model")

    draft = get_base_draft(
        name=draft_in.name or model["name"],
        description=draft_in.description or model["description"],
        source_type="model",
        workspace_id=workspace_id,
        user_id=user_id
    )
    draft["source_model_id"] = model_id
    draft["source_model_version"] = model.get("version", "1.0")

    # Pre-populate from model if possible
    if model.get("expected_stages"):
        draft["definition"]["stages"] = [
            {
                "stage_id": s.get("stage_id", new_id()),
                "name": s["name"],
                "description": s.get("description"),
                "sequence": s.get("sequence", i+1),
                "is_optional": s.get("is_optional", False)
            }
            for i, s in enumerate(model["expected_stages"])
        ]

    workflows_col.insert_one(draft)

    create_audit_event(
        workspace_id=workspace_id,
        actor_id=user_id,
        actor_role=context["role"],
        event_type="workflow_draft_created",
        entity_type="workflow",
        entity_id=draft["workflow_id"],
        metadata={"source_type": "model", "source_id": model_id}
    )

    return serialize_doc(draft)

@router.post("/draft/from-variant/{variant_id}", response_model=WorkflowDraftInDB)
def create_draft_from_variant(
    variant_id: str,
    draft_in: WorkflowDraftCreate,
    context: dict = Depends(deps.require_architect)
):
    """Create a workflow draft from a model variant."""
    workspace_id = context["workspace_id"]
    user_id = context["user"].user_id

    variant = model_variants_col.find_one({"variant_id": variant_id})
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    if variant.get("workspace_id") and variant.get("workspace_id") != workspace_id:
        raise HTTPException(status_code=403, detail="Access denied to this variant")

    model = process_models_col.find_one({"model_id": variant["model_id"]})

    draft = get_base_draft(
        name=draft_in.name or variant["name"],
        description=draft_in.description or variant.get("description", ""),
        source_type="variant",
        workspace_id=workspace_id,
        user_id=user_id
    )
    draft["source_model_id"] = variant["model_id"]
    draft["source_variant_id"] = variant_id
    draft["source_variant_version"] = variant.get("version", "1.0")

    # Pre-populate stages (combine model and variant)
    stages = []
    if model and model.get("expected_stages"):
        stages = model["expected_stages"]

    if variant.get("additional_stages"):
        stages.extend(variant["additional_stages"])

    # filter out removed optional stages
    removed = variant.get("removed_optional_stages", [])
    stages = [s for s in stages if s.get("stage_id") not in removed]

    draft["definition"]["stages"] = [
        {
            "stage_id": s.get("stage_id", new_id()),
            "name": s["name"],
            "description": s.get("description"),
            "sequence": s.get("sequence", i+1),
            "is_optional": s.get("is_optional", False)
        }
        for i, s in enumerate(stages)
    ]

    workflows_col.insert_one(draft)

    create_audit_event(
        workspace_id=workspace_id,
        actor_id=user_id,
        actor_role=context["role"],
        event_type="workflow_draft_created",
        entity_type="workflow",
        entity_id=draft["workflow_id"],
        metadata={"source_type": "variant", "source_id": variant_id}
    )

    return serialize_doc(draft)

@router.post("/draft/from-template/{template_id}", response_model=WorkflowDraftInDB)
def create_draft_from_template(
    template_id: str,
    draft_in: WorkflowDraftCreate,
    context: dict = Depends(deps.require_architect)
):
    """Create a workflow draft from a template."""
    workspace_id = context["workspace_id"]
    user_id = context["user"].user_id

    template = workflow_templates_col.find_one({"template_id": template_id})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    if template.get("source_type") != "global" and template.get("workspace_id") != workspace_id:
        raise HTTPException(status_code=403, detail="Access denied to this template")

    draft = get_base_draft(
        name=draft_in.name or template["name"],
        description=draft_in.description or template.get("description", ""),
        source_type="template",
        workspace_id=workspace_id,
        user_id=user_id
    )
    draft["source_model_id"] = template["process_model_id"]
    draft["source_variant_id"] = template.get("variant_id")
    draft["source_template_id"] = template_id
    draft["source_template_version"] = template.get("version", "1.0")

    # Copy template definition
    draft["definition"] = {
        "trigger": template.get("trigger_info") or draft["definition"]["trigger"],
        "inputs": template.get("input_definitions", []),
        "documents": [],
        "stages": template.get("stages", []),
        "steps": template.get("steps", []),
        "participants": [{"role": r, "assignment_method": "role"} for r in template.get("supported_roles", [])],
        "approvals": template.get("approval_placeholders", []),
        "notifications": template.get("notification_placeholders", []),
        "completion": {
            "valid_states": ["completed"],
            "required_outputs": [],
            "cancellation_behaviour": "cancel_pending",
            "incomplete_data_behaviour": "allow_completion"
        }
    }

    workflows_col.insert_one(draft)

    create_audit_event(
        workspace_id=workspace_id,
        actor_id=user_id,
        actor_role=context["role"],
        event_type="workflow_draft_created",
        entity_type="workflow",
        entity_id=draft["workflow_id"],
        metadata={"source_type": "template", "source_id": template_id}
    )

    return serialize_doc(draft)

@router.get("/drafts", response_model=List[WorkflowDraftList])
def list_drafts(
    context: dict = Depends(deps.get_workspace_context)
):
    """List workflow drafts in the current workspace."""
    workspace_id = context["workspace_id"]
    drafts = list(workflows_col.find({"workspace_id": workspace_id, "status": "draft"}).sort("updated_at", -1))
    return serialize_doc(drafts)

@router.get("/drafts/{workflow_id}", response_model=WorkflowDraftInDB)
def get_draft(
    workflow_id: str,
    context: dict = Depends(deps.get_workspace_context)
):
    """Get a specific workflow draft."""
    workspace_id = context["workspace_id"]
    draft = workflows_col.find_one({"workflow_id": workflow_id, "workspace_id": workspace_id})
    if not draft:
        raise HTTPException(status_code=404, detail="Workflow draft not found")
    return serialize_doc(draft)

@router.patch("/drafts/{workflow_id}", response_model=WorkflowDraftInDB)
def update_draft(
    workflow_id: str,
    draft_in: WorkflowDraftUpdate,
    context: dict = Depends(deps.require_architect)
):
    """Update a workflow draft."""
    workspace_id = context["workspace_id"]
    user_id = context["user"].user_id

    draft = workflows_col.find_one({"workflow_id": workflow_id, "workspace_id": workspace_id})
    if not draft:
        raise HTTPException(status_code=404, detail="Workflow draft not found")

    update_data = draft_in.model_dump(exclude_unset=True)
    update_data["updated_at"] = utcnow()
    update_data["updated_by"] = user_id

    # Handle nested definition update
    if "definition" in update_data:
        current_def = draft.get("definition", {})
        new_def_parts = update_data.pop("definition")
        for key, value in new_def_parts.items():
            current_def[key] = value
        update_data["definition"] = current_def

    workflows_col.update_one({"workflow_id": workflow_id}, {"$set": update_data})

    updated_draft = workflows_col.find_one({"workflow_id": workflow_id})
    return serialize_doc(updated_draft)

@router.post("/drafts/{workflow_id}/validate")
def validate_draft_endpoint(
    workflow_id: str,
    context: dict = Depends(deps.require_architect)
):
    """Validate a workflow draft."""
    workspace_id = context["workspace_id"]
    draft = workflows_col.find_one({"workflow_id": workflow_id, "workspace_id": workspace_id})
    if not draft:
        raise HTTPException(status_code=404, detail="Workflow draft not found")

    from backend.app.core.engine import validate_workflow
    issues = validate_workflow(draft)

    critical_count = sum(1 for i in issues if i["severity"] == "critical")
    validation_status = "valid" if critical_count == 0 else "invalid"

    workflows_col.update_one(
        {"workflow_id": workflow_id},
        {
            "$set": {
                "validation_results": issues,
                "validation_status": validation_status,
                "updated_at": utcnow()
            }
        }
    )

    return {
        "workflow_id": workflow_id,
        "validation_status": validation_status,
        "issues": issues
    }
