"""FlowForge AI - Phase 1 POC: Workflow Engine Core"""
import os
import uuid
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson import ObjectId

# ── Helpers ──────────────────────────────────────────────
def utcnow():
    return datetime.now(timezone.utc)

def new_id():
    return str(uuid.uuid4())

def serialize_doc(doc):
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(d) for d in doc]
    if isinstance(doc, dict):
        result = {}
        for k, v in doc.items():
            if isinstance(v, ObjectId):
                result[k] = str(v)
            elif isinstance(v, datetime):
                result[k] = v.isoformat()
            elif isinstance(v, dict):
                result[k] = serialize_doc(v)
            elif isinstance(v, list):
                result[k] = [serialize_doc(i) if isinstance(i, (dict, list)) else (str(i) if isinstance(i, ObjectId) else (i.isoformat() if isinstance(i, datetime) else i)) for i in v]
            else:
                result[k] = v
        return result
    return doc

# ── MongoDB ──────────────────────────────────────────────
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "flowforge_ai")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Collections
industries_col = db["industries"]
business_segments_col = db["business_segments"]
departments_col = db["departments"]
teams_col = db["teams"]
process_families_col = db["process_families"]
process_models_col = db["process_models"]
model_variants_col = db["model_variants"]
workflow_templates_col = db["workflow_templates"]
workflows_col = db["workflows"]
workflow_versions_col = db["workflow_versions"]
workflow_runs_col = db["workflow_runs"]
step_runs_col = db["step_runs"]
tasks_col = db["tasks"]
approvals_col = db["approvals"]
audit_events_col = db["audit_events"]
notifications_col = db["notifications"]
users_col = db["users"]
workspaces_col = db["workspaces"]
workspace_memberships_col = db["workspace_memberships"]
roles_col = db["roles"]
permissions_col = db["permissions"]

# ── Indexes ──────────────────────────────────────────────
def setup_indexes():
    process_models_col.create_index([("catalogue_status", ASCENDING)])
    process_models_col.create_index([("applicable_departments", ASCENDING)])
    process_models_col.create_index([("applicable_families", ASCENDING)])
    process_models_col.create_index([("tags", ASCENDING)])
    process_models_col.create_index([("workspace_id", ASCENDING)])
    workflows_col.create_index([("workspace_id", ASCENDING), ("status", ASCENDING)])
    workflow_versions_col.create_index([("workflow_id", ASCENDING), ("version", DESCENDING)])
    workflow_runs_col.create_index([("workspace_id", ASCENDING), ("status", ASCENDING)])
    workflow_runs_col.create_index([("workflow_version_id", ASCENDING)])
    step_runs_col.create_index([("run_id", ASCENDING), ("status", ASCENDING)])
    tasks_col.create_index([("workspace_id", ASCENDING), ("status", ASCENDING)])
    tasks_col.create_index([("assigned_role", ASCENDING), ("status", ASCENDING)])
    approvals_col.create_index([("workspace_id", ASCENDING), ("status", ASCENDING)])
    audit_events_col.create_index([("workspace_id", ASCENDING), ("timestamp", DESCENDING)])
    audit_events_col.create_index([("entity_type", ASCENDING), ("entity_id", ASCENDING)])
    audit_events_col.create_index([("run_id", ASCENDING)])

# ── Audit Helper ─────────────────────────────────────────
def create_audit_event(
    workspace_id: str,
    actor_id: str,
    actor_role: str,
    event_type: str,
    entity_type: str,
    entity_id: str,
    workflow_id: str = None,
    run_id: str = None,
    step_run_id: str = None,
    previous_state: dict = None,
    new_state: dict = None,
    metadata: dict = None,
    correlation_id: str = None,
):
    event = {
        "event_id": new_id(),
        "workspace_id": workspace_id,
        "actor_id": actor_id,
        "actor_role": actor_role,
        "event_type": event_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "workflow_id": workflow_id,
        "run_id": run_id,
        "step_run_id": step_run_id,
        "previous_state": previous_state or {},
        "new_state": new_state or {},
        "metadata": metadata or {},
        "correlation_id": correlation_id,
        "timestamp": utcnow(),
        "source": "system",
    }
    audit_events_col.insert_one(event)
    return event

# ── Notification Helper ──────────────────────────────────
def create_notification(
    workspace_id: str,
    recipient_role: str,
    recipient_id: str,
    notification_type: str,
    title: str,
    message: str,
    entity_type: str = None,
    entity_id: str = None,
    run_id: str = None,
):
    notif = {
        "notification_id": new_id(),
        "workspace_id": workspace_id,
        "recipient_role": recipient_role,
        "recipient_id": recipient_id,
        "notification_type": notification_type,
        "title": title,
        "message": message,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "run_id": run_id,
        "read": False,
        "created_at": utcnow(),
    }
    notifications_col.insert_one(notif)
    return notif

# ── Validation Engine ────────────────────────────────────
def validate_workflow(workflow: dict) -> List[dict]:
    """Validate a workflow definition. Returns list of validation issues."""
    issues = []
    defn = workflow.get("definition", {})
    
    # 1. Required metadata
    if not workflow.get("name"):
        issues.append({"severity": "critical", "category": "metadata", "section": "workflow", "message": "Workflow name is required", "step_id": None})
    if not workflow.get("owning_department"):
        issues.append({"severity": "warning", "category": "metadata", "section": "workflow", "message": "Owning department is not set", "step_id": None})
    
    # 2. Valid trigger
    trigger = defn.get("trigger", {})
    if not trigger.get("type"):
        issues.append({"severity": "critical", "category": "trigger", "section": "trigger", "message": "Trigger type is required", "step_id": None})
    
    # 3. Steps exist
    steps = defn.get("steps", [])
    if not steps:
        issues.append({"severity": "critical", "category": "steps", "section": "definition", "message": "Workflow must have at least one step", "step_id": None})
        return issues
    
    step_ids = {s["step_id"] for s in steps}
    
    # 4. Unique step IDs
    if len(step_ids) != len(steps):
        issues.append({"severity": "critical", "category": "steps", "section": "definition", "message": "Duplicate step IDs detected", "step_id": None})
    
    # 5. Stages exist
    stages = defn.get("stages", [])
    stage_ids = {s["stage_id"] for s in stages}
    if len(stage_ids) != len(stages):
        issues.append({"severity": "critical", "category": "stages", "section": "definition", "message": "Duplicate stage IDs detected", "step_id": None})
    
    # 6. Check each step
    has_end_step = False
    for step in steps:
        step_id = step.get("step_id")
        step_type = step.get("step_type")
        
        # Valid step type
        valid_types = ["form_input", "manual_task", "review", "approval", "condition", 
                       "notification", "data_write", "integration_action", "document_request",
                       "document_verification", "assignment", "wait", "escalation", 
                       "sub_workflow", "end"]
        if step_type not in valid_types:
            issues.append({"severity": "critical", "category": "step_type", "section": "steps", "message": f"Step '{step.get('name', step_id)}' has unsupported type: {step_type}", "step_id": step_id})
        
        if step_type == "end":
            has_end_step = True
        
        # Stage reference
        if step.get("stage_id") and step["stage_id"] not in stage_ids:
            issues.append({"severity": "warning", "category": "steps", "section": "steps", "message": f"Step '{step.get('name', step_id)}' references non-existent stage", "step_id": step_id})
        
        # Role assignment for human steps
        human_types = ["form_input", "manual_task", "review", "approval", "document_request"]
        if step_type in human_types and not step.get("assigned_role"):
            issues.append({"severity": "critical", "category": "roles", "section": "steps", "message": f"Step '{step.get('name', step_id)}' requires an assigned role", "step_id": step_id})
        
        # Approval must have assigned role
        if step_type == "approval" and not step.get("assigned_role"):
            issues.append({"severity": "critical", "category": "approval", "section": "steps", "message": f"Approval step '{step.get('name', step_id)}' missing approver role", "step_id": step_id})
        
        # Transition references
        transitions = step.get("transitions", {})
        for t_type, target_id in transitions.items():
            if target_id and target_id not in step_ids:
                issues.append({"severity": "critical", "category": "transitions", "section": "steps", "message": f"Step '{step.get('name', step_id)}' transition '{t_type}' references non-existent step '{target_id}'", "step_id": step_id})
        
        # Non-end steps must have at least success transition
        if step_type != "end" and not transitions.get("success"):
            issues.append({"severity": "critical", "category": "transitions", "section": "steps", "message": f"Step '{step.get('name', step_id)}' has no success transition", "step_id": step_id})
        
        # Approval steps should have rejection path
        if step_type == "approval" and not transitions.get("rejection"):
            issues.append({"severity": "warning", "category": "transitions", "section": "steps", "message": f"Approval step '{step.get('name', step_id)}' has no rejection path", "step_id": step_id})
    
    # 7. Reachable start step
    if steps and not steps[0].get("step_id"):
        issues.append({"severity": "critical", "category": "steps", "section": "definition", "message": "First step must have an ID", "step_id": None})
    
    # 8. Reachable completion state
    if not has_end_step:
        issues.append({"severity": "critical", "category": "completion", "section": "definition", "message": "Workflow must have at least one end step", "step_id": None})
    
    # 9. Reachability check - BFS from first step
    if steps:
        first_step_id = steps[0]["step_id"]
        visited = set()
        queue = [first_step_id]
        step_map = {s["step_id"]: s for s in steps}
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            step = step_map.get(current)
            if step:
                for target in step.get("transitions", {}).values():
                    if target and target not in visited:
                        queue.append(target)
        
        unreachable = step_ids - visited
        if unreachable:
            for ur_id in unreachable:
                ur_step = step_map.get(ur_id, {})
                issues.append({"severity": "warning", "category": "reachability", "section": "steps", "message": f"Step '{ur_step.get('name', ur_id)}' is unreachable from the start", "step_id": ur_id})
    
    # 10. Participants defined
    participants = defn.get("participants", [])
    required_roles = set()
    for step in steps:
        if step.get("assigned_role"):
            required_roles.add(step["assigned_role"])
    defined_roles = {p.get("role") for p in participants}
    missing_roles = required_roles - defined_roles
    if missing_roles:
        for role in missing_roles:
            issues.append({"severity": "warning", "category": "participants", "section": "participants", "message": f"Role '{role}' is used in steps but not defined as a participant", "step_id": None})
    
    return issues

# ── Workflow Execution Engine ────────────────────────────
def start_workflow_run(workflow_version: dict, run_inputs: dict, started_by: str, workspace_id: str) -> dict:
    """Start a new workflow run from a published version."""
    defn = workflow_version["definition_snapshot"]
    steps = defn.get("steps", [])
    correlation_id = new_id()
    
    run = {
        "run_id": new_id(),
        "workflow_id": workflow_version["workflow_id"],
        "workflow_version_id": workflow_version["version_id"],
        "workspace_id": workspace_id,
        "status": "running",
        "trigger_type": defn.get("trigger", {}).get("type", "manual"),
        "inputs": run_inputs,
        "outputs": {},
        "current_step_id": steps[0]["step_id"] if steps else None,
        "current_stage_id": steps[0].get("stage_id") if steps else None,
        "correlation_id": correlation_id,
        "started_by": started_by,
        "started_at": utcnow(),
        "completed_at": None,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    workflow_runs_col.insert_one(run)
    
    # Create step_run records for all steps
    for i, step in enumerate(steps):
        step_run = {
            "step_run_id": new_id(),
            "run_id": run["run_id"],
            "step_id": step["step_id"],
            "step_name": step.get("name", step["step_id"]),
            "step_type": step["step_type"],
            "stage_id": step.get("stage_id"),
            "status": "ready" if i == 0 else "pending",
            "assigned_role": step.get("assigned_role"),
            "assigned_to": None,
            "inputs": {},
            "outputs": {},
            "decision": None,
            "comments": None,
            "retry_count": 0,
            "started_at": utcnow() if i == 0 else None,
            "completed_at": None,
            "created_at": utcnow(),
            "updated_at": utcnow(),
        }
        step_runs_col.insert_one(step_run)
    
    # Audit
    create_audit_event(
        workspace_id=workspace_id,
        actor_id=started_by,
        actor_role="system",
        event_type="run_started",
        entity_type="workflow_run",
        entity_id=run["run_id"],
        workflow_id=workflow_version["workflow_id"],
        run_id=run["run_id"],
        new_state={"status": "running"},
        correlation_id=correlation_id,
    )
    
    # Process first step
    advance_run(run["run_id"], workspace_id)
    
    return serialize_doc(workflow_runs_col.find_one({"run_id": run["run_id"]}))


def advance_run(run_id: str, workspace_id: str):
    """Advance the workflow run by executing the current step."""
    run = workflow_runs_col.find_one({"run_id": run_id})
    if not run or run["status"] not in ["running", "waiting_input", "waiting_task", "waiting_approval"]:
        return
    
    current_step_id = run.get("current_step_id")
    if not current_step_id:
        return
    
    # Get the workflow version definition
    version = workflow_versions_col.find_one({"version_id": run["workflow_version_id"]})
    if not version:
        return
    
    defn = version["definition_snapshot"]
    step_map = {s["step_id"]: s for s in defn.get("steps", [])}
    current_step = step_map.get(current_step_id)
    if not current_step:
        return
    
    step_run = step_runs_col.find_one({"run_id": run_id, "step_id": current_step_id})
    if not step_run:
        return
    
    step_type = current_step["step_type"]
    
    # Auto-execute steps
    auto_types = ["notification", "data_write", "condition", "assignment", "end"]
    
    if step_type in auto_types:
        if step_type == "end":
            # Complete the run
            step_runs_col.update_one(
                {"step_run_id": step_run["step_run_id"]},
                {"$set": {"status": "completed", "completed_at": utcnow(), "updated_at": utcnow()}}
            )
            workflow_runs_col.update_one(
                {"run_id": run_id},
                {"$set": {"status": "completed", "completed_at": utcnow(), "current_step_id": None, "updated_at": utcnow()}}
            )
            create_audit_event(
                workspace_id=workspace_id,
                actor_id="system",
                actor_role="system",
                event_type="run_completed",
                entity_type="workflow_run",
                entity_id=run_id,
                workflow_id=run["workflow_id"],
                run_id=run_id,
                new_state={"status": "completed"},
                correlation_id=run.get("correlation_id"),
            )
            # Notification
            create_notification(
                workspace_id=workspace_id,
                recipient_role="workflow_owner",
                recipient_id=run.get("started_by", "system"),
                notification_type="workflow_completed",
                title="Workflow Completed",
                message=f"Workflow run has completed successfully.",
                entity_type="workflow_run",
                entity_id=run_id,
                run_id=run_id,
            )
            return
        
        elif step_type == "condition":
            # Evaluate condition
            config = current_step.get("config", {})
            condition_field = config.get("field", "")
            condition_operator = config.get("operator", "equals")
            condition_value = config.get("value", "")
            
            # Get the value from run inputs or step outputs
            actual_value = run.get("inputs", {}).get(condition_field) or run.get("outputs", {}).get(condition_field)
            
            condition_met = False
            if condition_operator == "equals":
                condition_met = str(actual_value) == str(condition_value)
            elif condition_operator == "not_equals":
                condition_met = str(actual_value) != str(condition_value)
            elif condition_operator == "greater_than":
                try:
                    condition_met = float(actual_value or 0) > float(condition_value)
                except (ValueError, TypeError):
                    condition_met = False
            elif condition_operator == "less_than":
                try:
                    condition_met = float(actual_value or 0) < float(condition_value)
                except (ValueError, TypeError):
                    condition_met = False
            elif condition_operator == "contains":
                condition_met = str(condition_value) in str(actual_value or "")
            
            step_runs_col.update_one(
                {"step_run_id": step_run["step_run_id"]},
                {"$set": {
                    "status": "completed",
                    "outputs": {"condition_result": condition_met, "evaluated_field": condition_field, "actual_value": str(actual_value)},
                    "completed_at": utcnow(),
                    "updated_at": utcnow(),
                }}
            )
            
            transitions = current_step.get("transitions", {})
            if condition_met:
                next_step_id = transitions.get("success")
            else:
                next_step_id = transitions.get("rejection") or transitions.get("failure") or transitions.get("success")
            
            if next_step_id:
                transition_to_step(run_id, next_step_id, workspace_id, run)
            return
        
        elif step_type == "notification":
            config = current_step.get("config", {})
            create_notification(
                workspace_id=workspace_id,
                recipient_role=config.get("recipient_role", "all"),
                recipient_id=config.get("recipient_id", "system"),
                notification_type="workflow_notification",
                title=config.get("title", "Workflow Notification"),
                message=config.get("message", "A workflow notification has been sent."),
                entity_type="workflow_run",
                entity_id=run_id,
                run_id=run_id,
            )
            step_runs_col.update_one(
                {"step_run_id": step_run["step_run_id"]},
                {"$set": {"status": "completed", "completed_at": utcnow(), "updated_at": utcnow()}}
            )
            transitions = current_step.get("transitions", {})
            next_step_id = transitions.get("success")
            if next_step_id:
                transition_to_step(run_id, next_step_id, workspace_id, run)
            return
        
        elif step_type in ["data_write", "assignment"]:
            step_runs_col.update_one(
                {"step_run_id": step_run["step_run_id"]},
                {"$set": {"status": "completed", "completed_at": utcnow(), "updated_at": utcnow()}}
            )
            transitions = current_step.get("transitions", {})
            next_step_id = transitions.get("success")
            if next_step_id:
                transition_to_step(run_id, next_step_id, workspace_id, run)
            return
    
    # Human steps - create task or approval and wait
    elif step_type == "approval":
        # Check if approval already exists
        existing = approvals_col.find_one({"run_id": run_id, "step_run_id": step_run["step_run_id"]})
        if not existing:
            approval = {
                "approval_id": new_id(),
                "run_id": run_id,
                "step_run_id": step_run["step_run_id"],
                "workflow_id": run["workflow_id"],
                "workspace_id": workspace_id,
                "title": f"Approval: {current_step.get('name', 'Approval Required')}",
                "description": current_step.get("description", "Please review and make a decision."),
                "assigned_role": current_step.get("assigned_role", "approver"),
                "assigned_to": None,
                "status": "pending",
                "context": {"run_inputs": run.get("inputs", {}), "step_config": current_step.get("config", {})},
                "submitted_data": {},
                "decision": None,
                "decision_comment": None,
                "decided_by": None,
                "decided_at": None,
                "created_at": utcnow(),
                "updated_at": utcnow(),
            }
            approvals_col.insert_one(approval)
            
            step_runs_col.update_one(
                {"step_run_id": step_run["step_run_id"]},
                {"$set": {"status": "waiting", "started_at": utcnow(), "updated_at": utcnow()}}
            )
            workflow_runs_col.update_one(
                {"run_id": run_id},
                {"$set": {"status": "waiting_approval", "updated_at": utcnow()}}
            )
            
            create_audit_event(
                workspace_id=workspace_id,
                actor_id="system",
                actor_role="system",
                event_type="approval_requested",
                entity_type="approval",
                entity_id=approval["approval_id"],
                workflow_id=run["workflow_id"],
                run_id=run_id,
                step_run_id=step_run["step_run_id"],
                new_state={"status": "pending", "assigned_role": approval["assigned_role"]},
                correlation_id=run.get("correlation_id"),
            )
            
            create_notification(
                workspace_id=workspace_id,
                recipient_role=current_step.get("assigned_role", "approver"),
                recipient_id="",
                notification_type="approval_request",
                title=f"New Approval Request: {current_step.get('name', 'Approval')}",
                message=f"An approval request is waiting for your decision.",
                entity_type="approval",
                entity_id=approval["approval_id"],
                run_id=run_id,
            )
    
    elif step_type in ["form_input", "manual_task", "review", "document_request"]:
        # Create task
        existing = tasks_col.find_one({"run_id": run_id, "step_run_id": step_run["step_run_id"]})
        if not existing:
            task = {
                "task_id": new_id(),
                "run_id": run_id,
                "step_run_id": step_run["step_run_id"],
                "workflow_id": run["workflow_id"],
                "workspace_id": workspace_id,
                "title": f"Task: {current_step.get('name', 'Task Required')}",
                "description": current_step.get("description", "Please complete this task."),
                "task_type": step_type,
                "assigned_role": current_step.get("assigned_role", "operator"),
                "assigned_to": None,
                "status": "pending",
                "required_inputs": current_step.get("config", {}).get("required_fields", []),
                "submitted_data": {},
                "priority": current_step.get("config", {}).get("priority", "normal"),
                "due_date": None,
                "completed_at": None,
                "created_at": utcnow(),
                "updated_at": utcnow(),
            }
            tasks_col.insert_one(task)
            
            step_runs_col.update_one(
                {"step_run_id": step_run["step_run_id"]},
                {"$set": {"status": "waiting", "started_at": utcnow(), "updated_at": utcnow()}}
            )
            workflow_runs_col.update_one(
                {"run_id": run_id},
                {"$set": {"status": "waiting_task", "updated_at": utcnow()}}
            )
            
            create_audit_event(
                workspace_id=workspace_id,
                actor_id="system",
                actor_role="system",
                event_type="task_created",
                entity_type="task",
                entity_id=task["task_id"],
                workflow_id=run["workflow_id"],
                run_id=run_id,
                step_run_id=step_run["step_run_id"],
                new_state={"status": "pending", "assigned_role": task["assigned_role"]},
                correlation_id=run.get("correlation_id"),
            )
            
            create_notification(
                workspace_id=workspace_id,
                recipient_role=current_step.get("assigned_role", "operator"),
                recipient_id="",
                notification_type="task_assignment",
                title=f"New Task: {current_step.get('name', 'Task')}",
                message=f"A new task has been assigned to your role.",
                entity_type="task",
                entity_id=task["task_id"],
                run_id=run_id,
            )


def transition_to_step(run_id: str, next_step_id: str, workspace_id: str, run: dict = None):
    """Transition the run to the next step."""
    if not run:
        run = workflow_runs_col.find_one({"run_id": run_id})
    
    # Update step run status
    next_step_run = step_runs_col.find_one({"run_id": run_id, "step_id": next_step_id})
    if next_step_run:
        step_runs_col.update_one(
            {"step_run_id": next_step_run["step_run_id"]},
            {"$set": {"status": "ready", "started_at": utcnow(), "updated_at": utcnow()}}
        )
    
    # Update run
    version = workflow_versions_col.find_one({"version_id": run["workflow_version_id"]})
    step_map = {s["step_id"]: s for s in version["definition_snapshot"]["steps"]}
    next_step = step_map.get(next_step_id, {})
    
    workflow_runs_col.update_one(
        {"run_id": run_id},
        {"$set": {
            "current_step_id": next_step_id,
            "current_stage_id": next_step.get("stage_id"),
            "status": "running",
            "updated_at": utcnow(),
        }}
    )
    
    create_audit_event(
        workspace_id=workspace_id,
        actor_id="system",
        actor_role="system",
        event_type="step_transition",
        entity_type="workflow_run",
        entity_id=run_id,
        workflow_id=run["workflow_id"],
        run_id=run_id,
        new_state={"current_step_id": next_step_id},
        correlation_id=run.get("correlation_id"),
    )
    
    # Advance the run
    advance_run(run_id, workspace_id)


# ── Pydantic Models ──────────────────────────────────────
class CreateWorkflowRequest(BaseModel):
    template_id: str
    workspace_id: str
    name: str
    description: str = ""
    owning_department: str = ""
    created_by: str = "system"

class StartRunRequest(BaseModel):
    workflow_version_id: str
    workspace_id: str
    inputs: dict = {}
    started_by: str = "system"

class CompleteTaskRequest(BaseModel):
    submitted_data: dict = {}
    completed_by: str = "system"

class ApprovalDecisionRequest(BaseModel):
    decision: str  # "approved" or "rejected"
    comment: str = ""
    decided_by: str = "system"

# ── App Setup ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_indexes()
    yield

app = FastAPI(title="FlowForge AI", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Health ───────────────────────────────────────────────
@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "FlowForge AI", "version": "0.1.0-poc"}

# ── POC: Seed ────────────────────────────────────────────
@app.post("/api/poc/seed")
def poc_seed():
    """Seed a sample process model + template for POC testing."""
    workspace_id = "poc-workspace"
    
    # Check if already seeded
    existing = process_models_col.find_one({"model_id": "poc-leave-approval-model"})
    if existing:
        return {"message": "Already seeded", "model_id": "poc-leave-approval-model", "template_id": "poc-leave-approval-template"}
    
    # Create process model
    model = {
        "model_id": "poc-leave-approval-model",
        "name": "Leave Approval Process",
        "description": "Standard leave approval process with manager and HR review.",
        "purpose": "Manage employee leave requests through structured approval workflow.",
        "source_type": "global",
        "ownership_scope": "platform",
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
        "model_owner": "platform",
        "workspace_id": None,
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
        "ownership_scope": "platform",
        "workspace_id": None,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    workflow_templates_col.insert_one(template)
    
    return {"message": "Seeded successfully", "model_id": "poc-leave-approval-model", "template_id": "poc-leave-approval-template"}

# ── POC: Create Workflow from Template ───────────────────
@app.post("/api/poc/workflows")
def create_workflow(req: CreateWorkflowRequest):
    """Create a new workflow from a template."""
    template = workflow_templates_col.find_one({"template_id": req.template_id})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    workflow_id = new_id()
    workflow = {
        "workflow_id": workflow_id,
        "workspace_id": req.workspace_id,
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
            "transitions": [],  # Transitions are embedded in steps
            "completion": {"valid_states": ["approved", "rejected"], "cancellation_behaviour": "cancel_pending_steps"},
        },
        "validation_results": [],
        "created_by": req.created_by,
        "updated_by": req.created_by,
        "created_at": utcnow(),
        "updated_at": utcnow(),
        "published_at": None,
        "archived_at": None,
    }
    workflows_col.insert_one(workflow)
    
    create_audit_event(
        workspace_id=req.workspace_id,
        actor_id=req.created_by,
        actor_role="process_architect",
        event_type="workflow_created",
        entity_type="workflow",
        entity_id=workflow_id,
        workflow_id=workflow_id,
        new_state={"status": "draft", "name": req.name},
    )
    
    return serialize_doc(workflows_col.find_one({"workflow_id": workflow_id}))

# ── POC: Validate Workflow ───────────────────────────────
@app.post("/api/poc/workflows/{workflow_id}/validate")
def validate_workflow_endpoint(workflow_id: str):
    """Validate a workflow definition."""
    workflow = workflows_col.find_one({"workflow_id": workflow_id})
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    issues = validate_workflow(workflow)
    
    critical_count = sum(1 for i in issues if i["severity"] == "critical")
    warning_count = sum(1 for i in issues if i["severity"] == "warning")
    
    new_status = workflow["status"]
    if critical_count == 0:
        new_status = "validated"
    else:
        new_status = "validation_required"
    
    workflows_col.update_one(
        {"workflow_id": workflow_id},
        {"$set": {"validation_results": issues, "status": new_status, "updated_at": utcnow()}}
    )
    
    create_audit_event(
        workspace_id=workflow.get("workspace_id", ""),
        actor_id="system",
        actor_role="system",
        event_type="workflow_validated",
        entity_type="workflow",
        entity_id=workflow_id,
        workflow_id=workflow_id,
        new_state={"status": new_status, "critical_issues": critical_count, "warnings": warning_count},
    )
    
    return {
        "workflow_id": workflow_id,
        "status": new_status,
        "valid": critical_count == 0,
        "critical_count": critical_count,
        "warning_count": warning_count,
        "issues": issues,
    }

# ── POC: Publish Workflow ────────────────────────────────
@app.post("/api/poc/workflows/{workflow_id}/publish")
def publish_workflow(workflow_id: str):
    """Publish a validated workflow, creating an immutable version."""
    workflow = workflows_col.find_one({"workflow_id": workflow_id})
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    if workflow["status"] not in ["validated", "draft"]:
        # Re-validate
        issues = validate_workflow(workflow)
        critical = [i for i in issues if i["severity"] == "critical"]
        if critical:
            raise HTTPException(status_code=400, detail=f"Cannot publish: {len(critical)} critical validation issues")
    
    # Auto-validate if draft
    if workflow["status"] == "draft":
        issues = validate_workflow(workflow)
        critical = [i for i in issues if i["severity"] == "critical"]
        if critical:
            raise HTTPException(status_code=400, detail=f"Cannot publish: {len(critical)} critical validation issues")
    
    version_number = workflow.get("version", 1)
    existing_versions = workflow_versions_col.count_documents({"workflow_id": workflow_id})
    version_number = existing_versions + 1
    
    version_id = new_id()
    version = {
        "version_id": version_id,
        "workflow_id": workflow_id,
        "version": version_number,
        "definition_snapshot": workflow["definition"],
        "published_by": workflow.get("updated_by", "system"),
        "published_at": utcnow(),
        "notes": f"Version {version_number}",
        "workspace_id": workflow.get("workspace_id"),
    }
    workflow_versions_col.insert_one(version)
    
    workflows_col.update_one(
        {"workflow_id": workflow_id},
        {"$set": {"status": "published", "version": version_number, "published_at": utcnow(), "updated_at": utcnow()}}
    )
    
    create_audit_event(
        workspace_id=workflow.get("workspace_id", ""),
        actor_id=workflow.get("updated_by", "system"),
        actor_role="process_architect",
        event_type="workflow_published",
        entity_type="workflow_version",
        entity_id=version_id,
        workflow_id=workflow_id,
        new_state={"version": version_number, "status": "published"},
    )
    
    return serialize_doc(workflow_versions_col.find_one({"version_id": version_id}))

# ── POC: Start Run ───────────────────────────────────────
@app.post("/api/poc/runs")
def start_run(req: StartRunRequest):
    """Start a workflow run from a published version."""
    version = workflow_versions_col.find_one({"version_id": req.workflow_version_id})
    if not version:
        raise HTTPException(status_code=404, detail="Workflow version not found")
    
    run = start_workflow_run(version, req.inputs, req.started_by, req.workspace_id)
    return run

# ── POC: Get Run ─────────────────────────────────────────
@app.get("/api/poc/runs/{run_id}")
def get_run(run_id: str):
    """Get workflow run details."""
    run = workflow_runs_col.find_one({"run_id": run_id})
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    step_runs = list(step_runs_col.find({"run_id": run_id}).sort("created_at", ASCENDING))
    run_tasks = list(tasks_col.find({"run_id": run_id}))
    run_approvals = list(approvals_col.find({"run_id": run_id}))
    
    return {
        "run": serialize_doc(run),
        "step_runs": serialize_doc(step_runs),
        "tasks": serialize_doc(run_tasks),
        "approvals": serialize_doc(run_approvals),
    }

# ── POC: Complete Task ───────────────────────────────────
@app.post("/api/poc/tasks/{task_id}/complete")
def complete_task(task_id: str, req: CompleteTaskRequest):
    """Complete a workflow task."""
    task = tasks_col.find_one({"task_id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task["status"] == "completed":
        raise HTTPException(status_code=400, detail="Task already completed")
    
    # Update task
    tasks_col.update_one(
        {"task_id": task_id},
        {"$set": {
            "status": "completed",
            "submitted_data": req.submitted_data,
            "completed_at": utcnow(),
            "updated_at": utcnow(),
        }}
    )
    
    # Update step run
    step_runs_col.update_one(
        {"step_run_id": task["step_run_id"]},
        {"$set": {
            "status": "completed",
            "outputs": req.submitted_data,
            "completed_at": utcnow(),
            "updated_at": utcnow(),
        }}
    )
    
    # Merge submitted data into run inputs for downstream conditions
    run = workflow_runs_col.find_one({"run_id": task["run_id"]})
    if run:
        merged_inputs = {**run.get("inputs", {}), **req.submitted_data}
        workflow_runs_col.update_one(
            {"run_id": task["run_id"]},
            {"$set": {"inputs": merged_inputs, "updated_at": utcnow()}}
        )
    
    # Audit
    create_audit_event(
        workspace_id=task.get("workspace_id", ""),
        actor_id=req.completed_by,
        actor_role=task.get("assigned_role", "operator"),
        event_type="task_completed",
        entity_type="task",
        entity_id=task_id,
        workflow_id=task.get("workflow_id"),
        run_id=task["run_id"],
        step_run_id=task["step_run_id"],
        previous_state={"status": "pending"},
        new_state={"status": "completed", "submitted_data": req.submitted_data},
    )
    
    # Get the step and transition to next
    version = workflow_versions_col.find_one({"version_id": run["workflow_version_id"]})
    if version:
        step_map = {s["step_id"]: s for s in version["definition_snapshot"]["steps"]}
        step_run = step_runs_col.find_one({"step_run_id": task["step_run_id"]})
        if step_run:
            step_def = step_map.get(step_run["step_id"])
            if step_def:
                next_step_id = step_def.get("transitions", {}).get("success")
                if next_step_id:
                    transition_to_step(task["run_id"], next_step_id, task.get("workspace_id", ""), run)
    
    return {"message": "Task completed", "task_id": task_id}

# ── POC: Approval Decision ───────────────────────────────
@app.post("/api/poc/approvals/{approval_id}/decide")
def decide_approval(approval_id: str, req: ApprovalDecisionRequest):
    """Make an approval decision."""
    approval = approvals_col.find_one({"approval_id": approval_id})
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    
    if approval["status"] != "pending":
        raise HTTPException(status_code=400, detail="Approval already decided")
    
    if req.decision not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Decision must be 'approved' or 'rejected'")
    
    # Update approval
    approvals_col.update_one(
        {"approval_id": approval_id},
        {"$set": {
            "status": req.decision,
            "decision": req.decision,
            "decision_comment": req.comment,
            "decided_by": req.decided_by,
            "decided_at": utcnow(),
            "updated_at": utcnow(),
        }}
    )
    
    # Update step run
    step_status = "approved" if req.decision == "approved" else "rejected"
    step_runs_col.update_one(
        {"step_run_id": approval["step_run_id"]},
        {"$set": {
            "status": step_status,
            "decision": req.decision,
            "comments": req.comment,
            "completed_at": utcnow(),
            "updated_at": utcnow(),
        }}
    )
    
    # Audit
    create_audit_event(
        workspace_id=approval.get("workspace_id", ""),
        actor_id=req.decided_by,
        actor_role=approval.get("assigned_role", "approver"),
        event_type="approval_decided",
        entity_type="approval",
        entity_id=approval_id,
        workflow_id=approval.get("workflow_id"),
        run_id=approval["run_id"],
        step_run_id=approval["step_run_id"],
        previous_state={"status": "pending"},
        new_state={"status": req.decision, "decision": req.decision, "comment": req.comment},
    )
    
    # Transition
    run = workflow_runs_col.find_one({"run_id": approval["run_id"]})
    if run:
        version = workflow_versions_col.find_one({"version_id": run["workflow_version_id"]})
        if version:
            step_map = {s["step_id"]: s for s in version["definition_snapshot"]["steps"]}
            step_run = step_runs_col.find_one({"step_run_id": approval["step_run_id"]})
            if step_run:
                step_def = step_map.get(step_run["step_id"])
                if step_def:
                    transitions = step_def.get("transitions", {})
                    if req.decision == "approved":
                        next_step_id = transitions.get("success")
                    else:
                        next_step_id = transitions.get("rejection") or transitions.get("failure")
                    
                    if next_step_id:
                        transition_to_step(approval["run_id"], next_step_id, approval.get("workspace_id", ""), run)
                    else:
                        # No transition - workflow may end
                        if req.decision == "rejected":
                            workflow_runs_col.update_one(
                                {"run_id": approval["run_id"]},
                                {"$set": {"status": "rejected", "completed_at": utcnow(), "updated_at": utcnow()}}
                            )
    
    return {"message": f"Approval {req.decision}", "approval_id": approval_id}

# ── POC: Get Audit Trail ─────────────────────────────────
@app.get("/api/poc/audit")
def get_audit(
    workspace_id: str = Query(default="poc-workspace"),
    run_id: str = Query(default=None),
    entity_type: str = Query(default=None),
    limit: int = Query(default=50, le=200),
    skip: int = Query(default=0),
):
    """Get audit events."""
    query = {"workspace_id": workspace_id}
    if run_id:
        query["run_id"] = run_id
    if entity_type:
        query["entity_type"] = entity_type
    
    total = audit_events_col.count_documents(query)
    events = list(audit_events_col.find(query).sort("timestamp", DESCENDING).skip(skip).limit(limit))
    
    return {"total": total, "events": serialize_doc(events)}

# ── POC: Get Tasks ───────────────────────────────────────
@app.get("/api/poc/tasks")
def get_tasks(
    workspace_id: str = Query(default="poc-workspace"),
    status: str = Query(default=None),
    assigned_role: str = Query(default=None),
    limit: int = Query(default=50),
):
    query = {"workspace_id": workspace_id}
    if status:
        query["status"] = status
    if assigned_role:
        query["assigned_role"] = assigned_role
    tasks = list(tasks_col.find(query).sort("created_at", DESCENDING).limit(limit))
    return {"tasks": serialize_doc(tasks)}

# ── POC: Get Approvals ───────────────────────────────────
@app.get("/api/poc/approvals")
def get_approvals(
    workspace_id: str = Query(default="poc-workspace"),
    status: str = Query(default=None),
    assigned_role: str = Query(default=None),
    limit: int = Query(default=50),
):
    query = {"workspace_id": workspace_id}
    if status:
        query["status"] = status
    if assigned_role:
        query["assigned_role"] = assigned_role
    approval_list = list(approvals_col.find(query).sort("created_at", DESCENDING).limit(limit))
    return {"approvals": serialize_doc(approval_list)}

# ── POC: Get Templates ───────────────────────────────────
@app.get("/api/poc/templates")
def get_templates():
    templates = list(workflow_templates_col.find({}))
    return {"templates": serialize_doc(templates)}

# ── POC: Get Workflows ───────────────────────────────────
@app.get("/api/poc/workflows")
def get_workflows(
    workspace_id: str = Query(default="poc-workspace"),
    status: str = Query(default=None),
):
    query = {"workspace_id": workspace_id}
    if status:
        query["status"] = status
    wfs = list(workflows_col.find(query).sort("created_at", DESCENDING))
    return {"workflows": serialize_doc(wfs)}

# ── POC: Get Workflow Versions ───────────────────────────
@app.get("/api/poc/workflows/{workflow_id}/versions")
def get_workflow_versions(workflow_id: str):
    versions = list(workflow_versions_col.find({"workflow_id": workflow_id}).sort("version", DESCENDING))
    return {"versions": serialize_doc(versions)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
