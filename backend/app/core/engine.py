from typing import List, Optional
from datetime import datetime, timezone
import uuid
from backend.app.core.utils import utcnow, new_id
from backend.app.db.mongodb import (
    process_models_col, workflows_col, workflow_versions_col,
    workflow_runs_col, step_runs_col, tasks_col, approvals_col,
    audit_events_col, notifications_col
)

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

    from backend.app.core.utils import serialize_doc
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
