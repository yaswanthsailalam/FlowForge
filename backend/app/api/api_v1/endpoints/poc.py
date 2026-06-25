from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from backend.app.api import deps
from backend.app.core.utils import utcnow, new_id, serialize_doc
from backend.app.db.mongodb import (
    industries_col, business_segments_col, departments_col,
    teams_col, process_families_col, process_models_col,
    workflow_templates_col, workflows_col,
    workflow_versions_col, workflow_runs_col, step_runs_col,
    tasks_col, approvals_col, audit_events_col
)
from backend.app.core import engine

router = APIRouter()

# ── Pydantic Models for Requests ─────────────────────────
class CreateWorkflowRequest(BaseModel):
    template_id: str
    name: str
    description: str = ""
    owning_department: str = ""

class StartRunRequest(BaseModel):
    workflow_version_id: str
    inputs: dict = {}

class CompleteTaskRequest(BaseModel):
    submitted_data: dict = {}

class ApprovalDecisionRequest(BaseModel):
    decision: str  # "approved" or "rejected"
    comment: str = ""

# ── Endpoints ────────────────────────────────────────────

def create_starter_model(model_id, name, description, industries=None, families=None, depts=None):
    return {
        "model_id": model_id,
        "workspace_id": None,
        "name": name,
        "description": description,
        "purpose": description,
        "source_type": "global",
        "ownership_scope": "global",
        "catalogue_status": "published",
        "publication_status": "published",
        "version": "1.0",
        "applicable_industries": industries or [],
        "applicable_segments": [],
        "applicable_departments": depts or [],
        "applicable_teams": [],
        "applicable_families": families or [],
        "tags": [name.lower().replace(" ", "-")],
        "stages": [
            {"stage_id": "initiation", "name": "Initiation", "sequence": 1},
            {"stage_id": "processing", "name": "Processing", "sequence": 2},
            {"stage_id": "completion", "name": "Completion", "sequence": 3},
        ],
        "suggested_roles": ["initiator", "reviewer", "approver"],
        "approval_points": ["final_approval"],
        "created_at": utcnow(),
        "updated_at": utcnow(),
        "published_at": utcnow(),
    }

@router.post("/seed")
def poc_seed(
    context: dict = Depends(deps.require_admin),
    _ = Depends(deps.require_poc_enabled)
):
    """Seed a comprehensive starter catalogue for POC testing."""
    workspace_id = context["workspace_id"]
    user_id = context["user"].user_id

    # 1. Industries
    industries = [
        ("ind-healthcare", "Healthcare"),
        ("ind-hr", "Human Resources"),
        ("ind-finance", "Finance"),
        ("ind-support", "Customer Support"),
        ("ind-procurement", "Procurement"),
        ("ind-supply-chain", "Supply Chain"),
    ]
    for iid, name in industries:
        if not industries_col.find_one({"industry_id": iid}):
            industries_col.insert_one({
                "industry_id": iid, "name": name, "description": f"{name} industry",
                "status": "active", "source_type": "global", "visibility": "public",
                "created_at": utcnow(), "updated_at": utcnow()
            })

    # 2. Departments
    depts = [
        ("dept-healthcare", "Healthcare Ops"),
        ("dept-hr", "Human Resources"),
        ("dept-finance", "Finance"),
        ("dept-support", "Customer Service"),
        ("dept-procurement", "Procurement"),
        ("dept-supply-chain", "Logistics"),
    ]
    for did, name in depts:
        if not departments_col.find_one({"department_id": did, "workspace_id": workspace_id}):
            departments_col.insert_one({
                "department_id": did, "workspace_id": workspace_id, "name": name,
                "description": f"{name} department", "status": "active",
                "created_at": utcnow(), "updated_at": utcnow()
            })

    # 3. Starter Process Models
    starter_models = [
        # Healthcare
        ("model-patient-referral", "Patient Referral Management", "ind-healthcare"),
        ("model-healthcare-vendor", "Healthcare Vendor Onboarding", "ind-healthcare"),
        ("model-clinical-doc", "Clinical Document Routing", "ind-healthcare"),
        # HR
        ("model-emp-onboarding", "Employee Onboarding", "ind-hr"),
        ("model-leave-approval", "Leave Approval", "ind-hr"),
        ("model-recruitment", "Recruitment Request", "ind-hr"),
        # Finance
        ("model-expense", "Expense Reimbursement", "ind-finance"),
        ("model-invoice", "Invoice Approval", "ind-finance"),
        ("model-budget", "Budget Request", "ind-finance"),
        # Customer Support
        ("model-complaint", "Complaint Handling", "ind-support"),
        ("model-ticket", "Ticket Escalation", "ind-support"),
        ("model-refund", "Refund Request", "ind-support"),
        # Procurement
        ("model-purchase", "Purchase Requisition", "ind-procurement"),
        ("model-vendor-reg", "Vendor Registration", "ind-procurement"),
        ("model-vendor-perf", "Vendor Performance Review", "ind-procurement"),
        # Supply Chain
        ("model-inventory", "Inventory Replenishment", "ind-supply-chain"),
        ("model-shipment", "Shipment Exception Handling", "ind-supply-chain"),
        ("model-stock-transfer", "Stock Transfer Request", "ind-supply-chain"),
    ]

    for mid, name, iid in starter_models:
        if not process_models_col.find_one({"model_id": mid}):
            model = create_starter_model(mid, name, f"Standard process for {name.lower()}.", industries=[iid])
            process_models_col.insert_one(model)

    # 4. Existing POC model (Legacy support)
    if not process_models_col.find_one({"model_id": "poc-leave-approval-model", "workspace_id": workspace_id}):
        model = {
            "model_id": "poc-leave-approval-model",
            "workspace_id": workspace_id,
            "name": "Leave Approval Process",
            "description": "Standard leave approval process with manager and HR review.",
            "purpose": "Manage employee leave requests through structured approval workflow.",
            "source_type": "global",
            "ownership_scope": "workspace",
            "catalogue_status": "published",
            "publication_status": "published",
            "version": "1.0",
            "applicable_industries": ["all"],
            "applicable_segments": [],
            "applicable_departments": ["human_resources"],
            "applicable_teams": [],
            "applicable_families": ["leave_management"],
            "tags": ["leave", "approval", "hr", "employee"],
            "stages": [
                {"stage_id": "submission", "name": "Submission", "sequence": 1},
                {"stage_id": "review", "name": "Review", "sequence": 2},
                {"stage_id": "completion", "name": "Completion", "sequence": 3},
            ],
            "suggested_roles": ["employee", "manager", "hr_admin"],
            "approval_points": ["manager_approval", "hr_approval"],
            "created_at": utcnow(),
            "updated_at": utcnow(),
            "published_at": utcnow(),
        }
        process_models_col.insert_one(model)

    # 5. Workflow Template for POC
    if not workflow_templates_col.find_one({"template_id": "poc-leave-approval-template", "workspace_id": workspace_id}):
        template = {
            "template_id": "poc-leave-approval-template",
            "workspace_id": workspace_id,
            "process_model_id": "poc-leave-approval-model",
            "name": "Standard Leave Approval Workflow",
            "description": "A standard leave approval workflow with manager and HR approval stages.",
            "trigger": {
                "trigger_id": "manual-trigger",
                "type": "manual",
                "name": "Manual Start",
                "config": {},
                "input_schema": {
                    "days_requested": {"type": "number", "required": True, "label": "Days Requested"},
                },
            },
            "stages": [
                {"stage_id": "submission", "name": "Submission", "sequence": 1, "steps": ["step_submit"]},
                {"stage_id": "review", "name": "Review", "sequence": 2, "steps": ["step_manager_approval"]},
                {"stage_id": "completion", "name": "Completion", "sequence": 3, "steps": ["step_end"]},
            ],
            "steps": [
                {
                    "step_id": "step_submit",
                    "name": "Submit Request",
                    "step_type": "form_input",
                    "assigned_role": "employee",
                    "stage_id": "submission",
                    "transitions": {"success": "step_manager_approval"}
                },
                {
                    "step_id": "step_manager_approval",
                    "name": "Manager Approval",
                    "step_type": "approval",
                    "assigned_role": "manager",
                    "stage_id": "review",
                    "transitions": {"success": "step_end", "rejection": "step_end"}
                },
                {
                    "step_id": "step_end",
                    "name": "End",
                    "step_type": "end",
                    "stage_id": "completion",
                    "transitions": {}
                }
            ],
            "roles": ["employee", "manager"],
            "publication_status": "published",
            "version": "1.0",
            "source_type": "workspace",
            "created_at": utcnow(),
            "updated_at": utcnow(),
        }
        workflow_templates_col.insert_one(template)

    return {"message": "Seeded successfully", "industries_seeded": len(industries), "models_seeded": len(starter_models)}

@router.get("/templates")
def get_templates(
    context: dict = Depends(deps.get_workspace_context),
    _ = Depends(deps.require_poc_enabled)
):
    workspace_id = context["workspace_id"]
    templates = list(workflow_templates_col.find({"workspace_id": workspace_id}))
    return {"templates": serialize_doc(templates)}

@router.post("/workflows")
def create_workflow(
    req: CreateWorkflowRequest,
    context: dict = Depends(deps.require_architect),
    _ = Depends(deps.require_poc_enabled)
):
    """Create a new workflow from a template."""
    workspace_id = context["workspace_id"]
    current_user = context["user"]

    template = workflow_templates_col.find_one({"template_id": req.template_id, "workspace_id": workspace_id})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    workflow_id = new_id()
    workflow = {
        "workflow_id": workflow_id,
        "workspace_id": workspace_id,
        "name": req.name,
        "description": req.description,
        "owning_department": req.owning_department,
        "participating_departments": [],
        "participating_teams": [],
        "process_model_id": template["process_model_id"],
        "model_version": "1.0",
        "variant_id": template.get("variant_id"),
        "template_id": req.template_id,
        "source_type": "template",
        "status": "draft",
        "version": 1,
        "definition": {
            "trigger": template.get("trigger", {}),
            "inputs": template.get("input_definitions", []),
            "participants": [{"role": r, "department": "", "team": "", "assignment_method": "role"} for r in template.get("roles", [])],
            "stages": template["stages"],
            "steps": template["steps"],
            "transitions": [],
            "completion": {"valid_states": ["approved", "rejected"], "cancellation_behaviour": "cancel_pending_steps"},
        },
        "validation_results": [],
        "created_by": current_user.user_id,
        "updated_by": current_user.user_id,
        "created_at": utcnow(),
        "updated_at": utcnow(),
        "published_at": None,
        "archived_at": None,
    }
    workflows_col.insert_one(workflow)

    engine.create_audit_event(
        workspace_id=workspace_id,
        actor_id=current_user.user_id,
        actor_role=context["role"],
        event_type="workflow_created",
        entity_type="workflow",
        entity_id=workflow_id,
        workflow_id=workflow_id,
        new_state={"status": "draft", "name": req.name},
    )

    return serialize_doc(workflows_col.find_one({"workflow_id": workflow_id}))

@router.get("/workflows")
def get_workflows(
    context: dict = Depends(deps.get_workspace_context),
    _ = Depends(deps.require_poc_enabled)
):
    workspace_id = context["workspace_id"]
    wfs = list(workflows_col.find({"workspace_id": workspace_id}).sort("created_at", -1))
    return {"workflows": serialize_doc(wfs)}

@router.get("/workflows/{workflow_id}/versions")
def get_workflow_versions(
    workflow_id: str,
    context: dict = Depends(deps.get_workspace_context),
    _ = Depends(deps.require_poc_enabled)
):
    workspace_id = context["workspace_id"]
    # Ensure workflow belongs to workspace
    workflow = workflows_col.find_one({"workflow_id": workflow_id, "workspace_id": workspace_id})
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    versions = list(workflow_versions_col.find({"workflow_id": workflow_id, "workspace_id": workspace_id}).sort("version", -1))
    return {"versions": serialize_doc(versions)}

@router.post("/workflows/{workflow_id}/validate")
def validate_workflow_endpoint(
    workflow_id: str,
    context: dict = Depends(deps.require_architect),
    _ = Depends(deps.require_poc_enabled)
):
    """Validate a workflow definition."""
    workspace_id = context["workspace_id"]
    workflow = workflows_col.find_one({"workflow_id": workflow_id, "workspace_id": workspace_id})
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    issues = engine.validate_workflow(workflow)

    critical_count = sum(1 for i in issues if i["severity"] == "critical")

    new_status = "validated" if critical_count == 0 else "validation_required"

    workflows_col.update_one(
        {"workflow_id": workflow_id},
        {"$set": {"validation_results": issues, "status": new_status, "updated_at": utcnow()}}
    )

    engine.create_audit_event(
        workspace_id=workspace_id,
        actor_id=context["user"].user_id,
        actor_role=context["role"],
        event_type="workflow_validated",
        entity_type="workflow",
        entity_id=workflow_id,
        workflow_id=workflow_id,
        new_state={"status": new_status, "critical_issues": critical_count},
    )

    return {
        "workflow_id": workflow_id,
        "status": new_status,
        "valid": critical_count == 0,
        "issues": issues,
    }

@router.post("/workflows/{workflow_id}/publish")
def publish_workflow(
    workflow_id: str,
    context: dict = Depends(deps.require_architect),
    _ = Depends(deps.require_poc_enabled)
):
    """Publish a validated workflow."""
    workspace_id = context["workspace_id"]
    workflow = workflows_col.find_one({"workflow_id": workflow_id, "workspace_id": workspace_id})
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Auto-validate
    issues = engine.validate_workflow(workflow)
    if any(i["severity"] == "critical" for i in issues):
        raise HTTPException(status_code=400, detail="Cannot publish: critical validation issues")

    version_number = workflow_versions_col.count_documents({"workflow_id": workflow_id}) + 1

    version_id = new_id()
    version = {
        "version_id": version_id,
        "workflow_id": workflow_id,
        "workspace_id": workspace_id,
        "version": version_number,
        "definition_snapshot": workflow["definition"],
        "published_by": context["user"].user_id,
        "published_at": utcnow(),
    }
    workflow_versions_col.insert_one(version)

    workflows_col.update_one(
        {"workflow_id": workflow_id},
        {"$set": {"status": "published", "version": version_number, "published_at": utcnow(), "updated_at": utcnow()}}
    )

    engine.create_audit_event(
        workspace_id=workspace_id,
        actor_id=context["user"].user_id,
        actor_role=context["role"],
        event_type="workflow_published",
        entity_type="workflow_version",
        entity_id=version_id,
        workflow_id=workflow_id,
        new_state={"version": version_number, "status": "published"},
    )

    return serialize_doc(version)

@router.post("/runs")
def start_run(
    req: StartRunRequest,
    context: dict = Depends(deps.require_operator),
    _ = Depends(deps.require_poc_enabled)
):
    """Start a workflow run."""
    workspace_id = context["workspace_id"]
    version = workflow_versions_col.find_one({"version_id": req.workflow_version_id, "workspace_id": workspace_id})
    if not version:
        raise HTTPException(status_code=404, detail="Workflow version not found")

    run = engine.start_workflow_run(version, req.inputs, context["user"].user_id, workspace_id)
    return run

@router.get("/runs/{run_id}")
def get_run(
    run_id: str,
    context: dict = Depends(deps.get_workspace_context),
    _ = Depends(deps.require_poc_enabled)
):
    """Get workflow run details."""
    workspace_id = context["workspace_id"]
    run = workflow_runs_col.find_one({"run_id": run_id, "workspace_id": workspace_id})
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    step_runs = list(step_runs_col.find({"run_id": run_id}).sort("created_at", 1))
    run_tasks = list(tasks_col.find({"run_id": run_id}))
    run_approvals = list(approvals_col.find({"run_id": run_id}))

    return {
        "run": serialize_doc(run),
        "step_runs": serialize_doc(step_runs),
        "tasks": serialize_doc(run_tasks),
        "approvals": serialize_doc(run_approvals),
    }

@router.get("/tasks")
def get_tasks(
    status: str = Query(default=None),
    assigned_role: str = Query(default=None),
    limit: int = Query(default=50),
    context: dict = Depends(deps.get_workspace_context),
    _ = Depends(deps.require_poc_enabled)
):
    workspace_id = context["workspace_id"]
    query = {"workspace_id": workspace_id}
    if status:
        query["status"] = status
    if assigned_role:
        query["assigned_role"] = assigned_role
    tasks = list(tasks_col.find(query).sort("created_at", -1).limit(limit))
    return {"tasks": serialize_doc(tasks)}

@router.post("/tasks/{task_id}/complete")
def complete_task(
    task_id: str,
    req: CompleteTaskRequest,
    context: dict = Depends(deps.require_operator),
    _ = Depends(deps.require_poc_enabled)
):
    """Complete a workflow task."""
    workspace_id = context["workspace_id"]
    current_user = context["user"]
    current_role = context["role"]

    task = tasks_col.find_one({"task_id": task_id, "workspace_id": workspace_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task["status"] != "pending":
        raise HTTPException(status_code=400, detail=f"Task is in invalid state for completion: {task['status']}")

    # Verify assignment: assigned user, assigned role, or workspace admin
    is_assigned_user = task.get("assigned_to") == current_user.user_id
    is_assigned_role = task.get("assigned_role") == current_role
    is_admin = current_role == "workspace_admin"

    if not (is_assigned_user or is_assigned_role or is_admin):
        raise HTTPException(status_code=403, detail="You are not authorized to complete this task")

    # Update task
    tasks_col.update_one(
        {"task_id": task_id},
        {"$set": {
            "status": "completed",
            "submitted_data": req.submitted_data,
            "completed_by": current_user.user_id,
            "completed_at": utcnow(),
            "updated_at": utcnow()
        }}
    )

    # Update step run
    step_runs_col.update_one(
        {"step_run_id": task["step_run_id"]},
        {"$set": {"status": "completed", "outputs": req.submitted_data, "completed_at": utcnow(), "updated_at": utcnow()}}
    )

    # Audit
    engine.create_audit_event(
        workspace_id=workspace_id,
        actor_id=current_user.user_id,
        actor_role=current_role,
        event_type="task_completed",
        entity_type="task",
        entity_id=task_id,
        workflow_id=task.get("workflow_id"),
        run_id=task["run_id"],
        step_run_id=task["step_run_id"],
        previous_state={"status": "pending"},
        new_state={"status": "completed", "submitted_data": req.submitted_data},
    )

    run = workflow_runs_col.find_one({"run_id": task["run_id"]})
    if run:
        merged_inputs = {**run.get("inputs", {}), **req.submitted_data}
        workflow_runs_col.update_one(
            {"run_id": task["run_id"]},
            {"$set": {"inputs": merged_inputs, "updated_at": utcnow(), "status": "running"}}
        )

        # Advance
        version = workflow_versions_col.find_one({"version_id": run["workflow_version_id"]})
        step_map = {s["step_id"]: s for s in version["definition_snapshot"]["steps"]}
        step_def = step_map.get(task["step_id"])
        if step_def:
            next_step_id = step_def.get("transitions", {}).get("success")
            if next_step_id:
                engine.transition_to_step(task["run_id"], next_step_id, workspace_id)

    return {"message": "Task completed"}

@router.get("/approvals")
def get_approvals(
    status: str = Query(default=None),
    assigned_role: str = Query(default=None),
    limit: int = Query(default=50),
    context: dict = Depends(deps.get_workspace_context),
    _ = Depends(deps.require_poc_enabled)
):
    workspace_id = context["workspace_id"]
    query = {"workspace_id": workspace_id}
    if status:
        query["status"] = status
    if assigned_role:
        query["assigned_role"] = assigned_role
    approval_list = list(approvals_col.find(query).sort("created_at", -1).limit(limit))
    return {"approvals": serialize_doc(approval_list)}

@router.post("/approvals/{approval_id}/decide")
def decide_approval(
    approval_id: str,
    req: ApprovalDecisionRequest,
    context: dict = Depends(deps.require_approver),
    _ = Depends(deps.require_poc_enabled)
):
    """Make an approval decision."""
    workspace_id = context["workspace_id"]
    current_user = context["user"]
    current_role = context["role"]

    approval = approvals_col.find_one({"approval_id": approval_id, "workspace_id": workspace_id})
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")

    if approval["status"] != "pending":
        raise HTTPException(status_code=400, detail=f"Approval is in invalid state: {approval['status']}")

    if req.decision not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Decision must be 'approved' or 'rejected'")

    # Verify assignment: assigned user, assigned role, or workspace admin
    is_assigned_user = approval.get("assigned_to") == current_user.user_id
    is_assigned_role = approval.get("assigned_role") == current_role
    is_admin = current_role == "workspace_admin"

    if not (is_assigned_user or is_assigned_role or is_admin):
        raise HTTPException(status_code=403, detail="You are not authorized to make a decision on this approval")

    # Update approval
    approvals_col.update_one(
        {"approval_id": approval_id},
        {"$set": {
            "status": req.decision,
            "decision": req.decision,
            "decision_comment": req.comment,
            "decided_by": current_user.user_id,
            "decided_at": utcnow(),
            "updated_at": utcnow()
        }}
    )

    # Update step run
    step_runs_col.update_one(
        {"step_run_id": approval["step_run_id"]},
        {"$set": {"status": req.decision, "completed_at": utcnow(), "updated_at": utcnow()}}
    )

    # Audit
    engine.create_audit_event(
        workspace_id=workspace_id,
        actor_id=current_user.user_id,
        actor_role=current_role,
        event_type="approval_decided",
        entity_type="approval",
        entity_id=approval_id,
        workflow_id=approval.get("workflow_id"),
        run_id=approval["run_id"],
        step_run_id=approval["step_run_id"],
        previous_state={"status": "pending"},
        new_state={"status": req.decision, "decision": req.decision},
        metadata={"comment": req.comment}
    )

    run = workflow_runs_col.find_one({"run_id": approval["run_id"]})
    if run:
        version = workflow_versions_col.find_one({"version_id": run["workflow_version_id"]})
        step_map = {s["step_id"]: s for s in version["definition_snapshot"]["steps"]}
        step_run = step_runs_col.find_one({"step_run_id": approval["step_run_id"]})
        step_def = step_map.get(step_run["step_id"])

        transitions = step_def.get("transitions", {})
        next_step_id = transitions.get("success") if req.decision == "approved" else (transitions.get("rejection") or transitions.get("failure"))

        if next_step_id:
            engine.transition_to_step(run["run_id"], next_step_id, workspace_id)
        elif req.decision == "rejected":
             workflow_runs_col.update_one({"run_id": run["run_id"]}, {"$set": {"status": "rejected", "completed_at": utcnow()}})

    return {"message": f"Approval {req.decision}"}

@router.get("/audit")
def get_audit(
    run_id: str = Query(default=None),
    entity_type: str = Query(default=None),
    limit: int = Query(default=50, le=200),
    skip: int = Query(default=0),
    context: dict = Depends(deps.get_workspace_context),
    _ = Depends(deps.require_poc_enabled)
):
    """Get audit events."""
    workspace_id = context["workspace_id"]
    query = {"workspace_id": workspace_id}
    if run_id:
        query["run_id"] = run_id
    if entity_type:
        query["entity_type"] = entity_type

    total = audit_events_col.count_documents(query)
    events = list(audit_events_col.find(query).sort("timestamp", -1).skip(skip).limit(limit))

    return {"total": total, "events": serialize_doc(events)}
