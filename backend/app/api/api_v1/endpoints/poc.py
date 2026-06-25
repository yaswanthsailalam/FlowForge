from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from backend.app.api import deps
from backend.app.core.utils import utcnow, new_id, serialize_doc
from backend.app.db.mongodb import (
    process_models_col, workflow_templates_col, workflows_col,
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

@router.post("/seed")
def poc_seed(
    context: dict = Depends(deps.require_admin),
    _ = Depends(deps.require_poc_enabled)
):
    """Seed a sample process model + template for POC testing."""
    workspace_id = context["workspace_id"]

    existing = process_models_col.find_one({"model_id": "poc-leave-approval-model", "workspace_id": workspace_id})
    if existing:
        return {"message": "Already seeded", "model_id": "poc-leave-approval-model"}

    # Create process model
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
        "keywords": ["leave request", "vacation", "sick leave", "approval"],
        "stages": [
            {"stage_id": "submission", "name": "Submission", "description": "Employee submits leave request", "sequence": 1},
            {"stage_id": "review", "name": "Review", "description": "Manager and HR review the request", "sequence": 2},
            {"stage_id": "completion", "name": "Completion", "description": "Final notification and completion", "sequence": 3},
        ],
        "suggested_roles": ["employee", "manager", "hr_admin"],
        "approval_points": ["manager_approval", "hr_approval"],
        "decision_paths": [{"decision": "approve_or_reject", "paths": ["approved", "rejected"]}],
        "required_config_sections": ["trigger", "inputs", "roles", "approvals"],
        "supported_input_types": ["text", "date", "select"],
        "expected_output_types": ["approval_status", "notification"],
        "exception_categories": ["rejection", "timeout"],
        "completion_conditions": ["all_approvals_received"],
        "validation_rules": [],
        "model_owner": context["user"].user_id,
        "parent_model_id": None,
        "replacement_model_id": None,
        "deprecated": False,
        "created_at": utcnow(),
        "updated_at": utcnow(),
        "published_at": utcnow(),
        "archived_at": None,
    }
    process_models_col.insert_one(model)

    # Create workflow template
    template = {
        "template_id": "poc-leave-approval-template",
        "workspace_id": workspace_id,
        "process_model_id": "poc-leave-approval-model",
        "variant_id": None,
        "name": "Standard Leave Approval Workflow",
        "description": "A standard leave approval workflow with manager and HR approval stages.",
        "applicability": {"industries": ["all"], "departments": ["human_resources"]},
        "trigger": {
            "trigger_id": "manual-trigger",
            "type": "manual",
            "name": "Manual Start",
            "config": {},
            "input_schema": {
                "employee_name": {"type": "text", "required": True, "label": "Employee Name"},
                "leave_type": {"type": "select", "required": True, "label": "Leave Type", "options": ["annual", "sick", "personal", "unpaid"]},
                "start_date": {"type": "date", "required": True, "label": "Start Date"},
                "end_date": {"type": "date", "required": True, "label": "End Date"},
                "days_requested": {"type": "number", "required": True, "label": "Days Requested"},
                "reason": {"type": "text", "required": False, "label": "Reason"},
            },
        },
        "stages": [
            {"stage_id": "submission", "name": "Submission", "description": "Employee submits leave request", "sequence": 1, "steps": ["step_submit"]},
            {"stage_id": "review", "name": "Review", "description": "Manager and HR review", "sequence": 2, "steps": ["step_check_days", "step_manager_approval", "step_hr_approval"]},
            {"stage_id": "completion", "name": "Completion", "description": "Final notification", "sequence": 3, "steps": ["step_notify_approved", "step_notify_rejected", "step_end_approved", "step_end_rejected"]},
        ],
        "steps": [
            {
                "step_id": "step_submit",
                "name": "Submit Leave Request",
                "description": "Employee fills in the leave request form.",
                "step_type": "form_input",
                "stage_id": "submission",
                "assigned_role": "employee",
                "assignment_method": "role",
                "config": {
                    "required_fields": [
                        {"key": "employee_name", "label": "Employee Name", "type": "text", "required": True},
                        {"key": "leave_type", "label": "Leave Type", "type": "select", "required": True},
                        {"key": "start_date", "label": "Start Date", "type": "date", "required": True},
                        {"key": "end_date", "label": "End Date", "type": "date", "required": True},
                        {"key": "days_requested", "label": "Days Requested", "type": "number", "required": True},
                        {"key": "reason", "label": "Reason", "type": "text", "required": False},
                    ],
                },
                "input_mapping": {},
                "output_mapping": {"leave_request": "submitted_data"},
                "entry_conditions": [],
                "transitions": {"success": "step_check_days", "rejection": None, "failure": None},
                "timeout_config": {},
                "retry_config": {},
                "required": True,
            },
            {
                "step_id": "step_check_days",
                "name": "Check Days Threshold",
                "description": "Check if leave days exceed threshold for HR approval.",
                "step_type": "condition",
                "stage_id": "review",
                "assigned_role": None,
                "assignment_method": None,
                "config": {"field": "days_requested", "operator": "greater_than", "value": "3"},
                "input_mapping": {},
                "output_mapping": {},
                "entry_conditions": [],
                "transitions": {"success": "step_hr_approval", "rejection": "step_manager_approval", "failure": "step_manager_approval"},
                "timeout_config": {},
                "retry_config": {},
                "required": True,
            },
            {
                "step_id": "step_manager_approval",
                "name": "Manager Approval",
                "description": "Direct manager reviews and approves/rejects the request.",
                "step_type": "approval",
                "stage_id": "review",
                "assigned_role": "manager",
                "assignment_method": "role",
                "config": {},
                "input_mapping": {},
                "output_mapping": {},
                "entry_conditions": [],
                "transitions": {"success": "step_notify_approved", "rejection": "step_notify_rejected", "failure": None},
                "timeout_config": {},
                "retry_config": {},
                "required": True,
            },
            {
                "step_id": "step_hr_approval",
                "name": "HR Approval",
                "description": "HR department reviews and approves/rejects extended leave.",
                "step_type": "approval",
                "stage_id": "review",
                "assigned_role": "hr_admin",
                "assignment_method": "role",
                "config": {},
                "input_mapping": {},
                "output_mapping": {},
                "entry_conditions": [],
                "transitions": {"success": "step_manager_approval", "rejection": "step_notify_rejected", "failure": None},
                "timeout_config": {},
                "retry_config": {},
                "required": True,
            },
            {
                "step_id": "step_notify_approved",
                "name": "Send Approval Notification",
                "description": "Notify the employee that their leave has been approved.",
                "step_type": "notification",
                "stage_id": "completion",
                "assigned_role": None,
                "assignment_method": None,
                "config": {"recipient_role": "employee", "title": "Leave Approved", "message": "Your leave request has been approved."},
                "input_mapping": {},
                "output_mapping": {},
                "entry_conditions": [],
                "transitions": {"success": "step_end_approved", "rejection": None, "failure": None},
                "timeout_config": {},
                "retry_config": {},
                "required": True,
            },
            {
                "step_id": "step_notify_rejected",
                "name": "Send Rejection Notification",
                "description": "Notify the employee that their leave has been rejected.",
                "step_type": "notification",
                "stage_id": "completion",
                "assigned_role": None,
                "assignment_method": None,
                "config": {"recipient_role": "employee", "title": "Leave Rejected", "message": "Your leave request has been rejected."},
                "input_mapping": {},
                "output_mapping": {},
                "entry_conditions": [],
                "transitions": {"success": "step_end_rejected", "rejection": None, "failure": None},
                "timeout_config": {},
                "retry_config": {},
                "required": True,
            },
            {
                "step_id": "step_end_approved",
                "name": "End - Approved",
                "description": "Workflow completes with approval.",
                "step_type": "end",
                "stage_id": "completion",
                "assigned_role": None,
                "assignment_method": None,
                "config": {"completion_status": "approved"},
                "input_mapping": {},
                "output_mapping": {},
                "entry_conditions": [],
                "transitions": {},
                "timeout_config": {},
                "retry_config": {},
                "required": True,
            },
            {
                "step_id": "step_end_rejected",
                "name": "End - Rejected",
                "description": "Workflow completes with rejection.",
                "step_type": "end",
                "stage_id": "completion",
                "assigned_role": None,
                "assignment_method": None,
                "config": {"completion_status": "rejected"},
                "input_mapping": {},
                "output_mapping": {},
                "entry_conditions": [],
                "transitions": {},
                "timeout_config": {},
                "retry_config": {},
                "required": True,
            },
        ],
        "roles": ["employee", "manager", "hr_admin"],
        "input_definitions": [
            {"key": "employee_name", "label": "Employee Name", "type": "text", "required": True},
            {"key": "leave_type", "label": "Leave Type", "type": "select", "required": True, "options": ["annual", "sick", "personal", "unpaid"]},
            {"key": "start_date", "label": "Start Date", "type": "date", "required": True},
            {"key": "end_date", "label": "End Date", "type": "date", "required": True},
            {"key": "days_requested", "label": "Days Requested", "type": "number", "required": True},
            {"key": "reason", "label": "Reason", "type": "text", "required": False},
        ],
        "output_definitions": [{"key": "approval_status", "type": "text"}],
        "visibility": "public",
        "publication_status": "published",
        "version": "1.0",
        "source": "platform",
        "ownership_scope": "workspace",
        "workspace_id": workspace_id,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    workflow_templates_col.insert_one(template)

    return {"message": "Seeded successfully", "model_id": "poc-leave-approval-model", "template_id": "poc-leave-approval-template"}

@router.get("/templates")
def get_templates(context: dict = Depends(deps.get_workspace_context)):
    workspace_id = context["workspace_id"]
    templates = list(workflow_templates_col.find({"workspace_id": workspace_id}))
    return {"templates": serialize_doc(templates)}

@router.post("/workflows")
def create_workflow(
    req: CreateWorkflowRequest,
    context: dict = Depends(deps.require_architect)
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
            "trigger": template["trigger"],
            "inputs": template["input_definitions"],
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
def get_workflows(context: dict = Depends(deps.get_workspace_context)):
    workspace_id = context["workspace_id"]
    wfs = list(workflows_col.find({"workspace_id": workspace_id}).sort("created_at", -1))
    return {"workflows": serialize_doc(wfs)}

@router.get("/workflows/{workflow_id}/versions")
def get_workflow_versions(
    workflow_id: str,
    context: dict = Depends(deps.get_workspace_context)
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
    context: dict = Depends(deps.require_architect)
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
    context: dict = Depends(deps.require_architect)
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
    context: dict = Depends(deps.require_operator)
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
    context: dict = Depends(deps.get_workspace_context)
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
    context: dict = Depends(deps.get_workspace_context)
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
    context: dict = Depends(deps.require_operator)
):
    """Complete a workflow task."""
    workspace_id = context["workspace_id"]
    task = tasks_col.find_one({"task_id": task_id, "workspace_id": workspace_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task["status"] == "completed":
        raise HTTPException(status_code=400, detail="Task already completed")

    tasks_col.update_one(
        {"task_id": task_id},
        {"$set": {"status": "completed", "submitted_data": req.submitted_data, "completed_at": utcnow(), "updated_at": utcnow()}}
    )

    step_runs_col.update_one(
        {"step_run_id": task["step_run_id"]},
        {"$set": {"status": "completed", "outputs": req.submitted_data, "completed_at": utcnow(), "updated_at": utcnow()}}
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
    context: dict = Depends(deps.get_workspace_context)
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
    context: dict = Depends(deps.require_approver)
):
    """Make an approval decision."""
    workspace_id = context["workspace_id"]
    approval = approvals_col.find_one({"approval_id": approval_id, "workspace_id": workspace_id})
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")

    if approval["status"] != "pending":
        raise HTTPException(status_code=400, detail="Approval already decided")

    approvals_col.update_one(
        {"approval_id": approval_id},
        {"$set": {"status": req.decision, "decision": req.decision, "decided_by": context["user"].user_id, "decided_at": utcnow()}}
    )

    step_runs_col.update_one(
        {"step_run_id": approval["step_run_id"]},
        {"$set": {"status": req.decision, "completed_at": utcnow()}}
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
    context: dict = Depends(deps.get_workspace_context)
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
