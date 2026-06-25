"""FlowForge AI - Phase 1 POC Test Script
Tests the complete workflow engine: Seed → Create → Validate → Publish → Execute → Tasks → Approvals → Audit
Also tests GPT-4o integration.
"""
import os
import sys
import json
import requests
import asyncio
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8001/api"

def print_result(test_name, success, details=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"\n{status}: {test_name}")
    if details:
        print(f"   {details}")
    return success

def test_health():
    r = requests.get(f"{BASE_URL}/health")
    return print_result("Health Check", r.status_code == 200, f"Status: {r.json().get('status')}")

def test_seed():
    r = requests.post(f"{BASE_URL}/poc/seed")
    data = r.json()
    return print_result("Seed Process Model & Template", r.status_code == 200, f"Model: {data.get('model_id')}, Template: {data.get('template_id')}")

def test_create_workflow():
    r = requests.post(f"{BASE_URL}/poc/workflows", json={
        "template_id": "poc-leave-approval-template",
        "workspace_id": "poc-workspace",
        "name": "Q1 Leave Approval Workflow",
        "description": "Leave approval for Q1 2025",
        "owning_department": "human_resources",
        "created_by": "poc-user",
    })
    data = r.json()
    success = r.status_code == 200 and data.get("status") == "draft"
    workflow_id = data.get("workflow_id")
    return print_result("Create Workflow from Template", success, f"Workflow ID: {workflow_id}, Status: {data.get('status')}"), workflow_id

def test_validate_workflow(workflow_id):
    r = requests.post(f"{BASE_URL}/poc/workflows/{workflow_id}/validate")
    data = r.json()
    success = r.status_code == 200 and data.get("valid") == True
    return print_result("Validate Workflow", success, f"Valid: {data.get('valid')}, Critical: {data.get('critical_count')}, Warnings: {data.get('warning_count')}")

def test_publish_workflow(workflow_id):
    r = requests.post(f"{BASE_URL}/poc/workflows/{workflow_id}/publish")
    data = r.json()
    success = r.status_code == 200 and data.get("version_id")
    version_id = data.get("version_id")
    return print_result("Publish Workflow (Immutable Version)", success, f"Version ID: {version_id}, Version #: {data.get('version')}"), version_id

def test_start_run(version_id, days_requested=2):
    """Start a run. days_requested controls condition branch."""
    r = requests.post(f"{BASE_URL}/poc/runs", json={
        "workflow_version_id": version_id,
        "workspace_id": "poc-workspace",
        "inputs": {
            "employee_name": "John Doe",
            "leave_type": "annual",
            "start_date": "2025-02-01",
            "end_date": "2025-02-03" if days_requested <= 3 else "2025-02-10",
            "days_requested": str(days_requested),
            "reason": "Family vacation",
        },
        "started_by": "poc-user",
    })
    data = r.json()
    run_id = data.get("run_id")
    status = data.get("status")
    success = r.status_code == 200 and run_id
    return print_result(f"Start Workflow Run (days={days_requested})", success, f"Run ID: {run_id}, Status: {status}"), run_id

def test_get_run(run_id):
    r = requests.get(f"{BASE_URL}/poc/runs/{run_id}")
    data = r.json()
    run = data.get("run", {})
    step_runs = data.get("step_runs", [])
    tasks = data.get("tasks", [])
    apprs = data.get("approvals", [])
    
    print(f"\n📋 Run Status: {run.get('status')}")
    print(f"   Current Step: {run.get('current_step_id')}")
    print(f"   Step Runs: {len(step_runs)}")
    for sr in step_runs:
        print(f"     - {sr.get('step_name')}: {sr.get('status')} ({sr.get('step_type')})")
    print(f"   Tasks: {len(tasks)}")
    for t in tasks:
        print(f"     - {t.get('title')}: {t.get('status')}")
    print(f"   Approvals: {len(apprs)}")
    for a in apprs:
        print(f"     - {a.get('title')}: {a.get('status')}")
    
    return data

def test_complete_task(run_id):
    """Find and complete the pending task for this run."""
    r = requests.get(f"{BASE_URL}/poc/runs/{run_id}")
    data = r.json()
    tasks = data.get("tasks", [])
    pending_tasks = [t for t in tasks if t.get("status") == "pending"]
    
    if not pending_tasks:
        return print_result("Complete Task", False, "No pending tasks found")
    
    task = pending_tasks[0]
    task_id = task["task_id"]
    
    # Get the run to preserve existing inputs
    run_data = requests.get(f"{BASE_URL}/poc/runs/{run_id}").json()
    run_inputs = run_data.get("run", {}).get("inputs", {})
    
    r2 = requests.post(f"{BASE_URL}/poc/tasks/{task_id}/complete", json={
        "submitted_data": {
            "employee_name": run_inputs.get("employee_name", "John Doe"),
            "leave_type": run_inputs.get("leave_type", "annual"),
            "start_date": run_inputs.get("start_date", "2025-02-01"),
            "end_date": run_inputs.get("end_date", "2025-02-03"),
            "days_requested": run_inputs.get("days_requested", "2"),
            "reason": run_inputs.get("reason", "Family vacation"),
        },
        "completed_by": "poc-user",
    })
    success = r2.status_code == 200
    return print_result("Complete Task (Form Submission)", success, f"Task: {task.get('title')}")

def test_approve(run_id, role_filter=None):
    """Find and approve the pending approval for this run."""
    r = requests.get(f"{BASE_URL}/poc/runs/{run_id}")
    data = r.json()
    apprs = data.get("approvals", [])
    pending = [a for a in apprs if a.get("status") == "pending"]
    
    if role_filter:
        pending = [a for a in pending if a.get("assigned_role") == role_filter]
    
    if not pending:
        return print_result(f"Approve ({role_filter or 'any'})", False, "No pending approvals found")
    
    approval = pending[0]
    approval_id = approval["approval_id"]
    
    r2 = requests.post(f"{BASE_URL}/poc/approvals/{approval_id}/decide", json={
        "decision": "approved",
        "comment": f"Approved by {role_filter or 'approver'}",
        "decided_by": f"poc-{role_filter or 'approver'}",
    })
    success = r2.status_code == 200
    return print_result(f"Approve ({role_filter or 'any'})", success, f"Approval: {approval.get('title')}")

def test_reject(run_id, role_filter=None):
    """Find and reject the pending approval for this run."""
    r = requests.get(f"{BASE_URL}/poc/runs/{run_id}")
    data = r.json()
    apprs = data.get("approvals", [])
    pending = [a for a in apprs if a.get("status") == "pending"]
    
    if role_filter:
        pending = [a for a in pending if a.get("assigned_role") == role_filter]
    
    if not pending:
        return print_result(f"Reject ({role_filter or 'any'})", False, "No pending approvals found")
    
    approval = pending[0]
    approval_id = approval["approval_id"]
    
    r2 = requests.post(f"{BASE_URL}/poc/approvals/{approval_id}/decide", json={
        "decision": "rejected",
        "comment": f"Rejected by {role_filter or 'approver'}",
        "decided_by": f"poc-{role_filter or 'approver'}",
    })
    success = r2.status_code == 200
    return print_result(f"Reject ({role_filter or 'any'})", success, f"Approval: {approval.get('title')}")

def test_audit_trail(run_id):
    r = requests.get(f"{BASE_URL}/poc/audit", params={"run_id": run_id})
    data = r.json()
    events = data.get("events", [])
    print(f"\n📜 Audit Trail ({len(events)} events):")
    for e in events:
        print(f"   [{e.get('event_type')}] {e.get('entity_type')}:{e.get('entity_id', '')[:8]}... | Actor: {e.get('actor_id')}")
    return print_result("Audit Trail", len(events) > 0, f"{len(events)} events recorded")

def test_gpt4o():
    """Test GPT-4o integration via emergentintegrations."""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            return print_result("GPT-4o Integration", False, "EMERGENT_LLM_KEY not set")
        
        chat = LlmChat(
            api_key=api_key,
            session_id="poc-test-ai",
            system_message="You are a workflow assistant. Respond with JSON only."
        ).with_model("openai", "gpt-4o")
        
        user_msg = UserMessage(
            text='Given a leave approval workflow, suggest 3 optional steps that could improve it. Respond as JSON: {"suggestions": [{"name": "...", "description": "...", "step_type": "..."}]}'
        )
        
        # Use send_message for non-streaming test
        response = asyncio.run(chat.send_message(user_msg))
        
        if response:
            resp_text = response.text if hasattr(response, 'text') else str(response)
            print(f"   AI Response: {resp_text[:200]}...")
            return print_result("GPT-4o Integration", True, "AI responded with suggestions")
        else:
            return print_result("GPT-4o Integration", False, f"Unexpected response: {response}")
    except Exception as e:
        return print_result("GPT-4o Integration", False, f"Error: {str(e)}")

def run_all_tests():
    print("="*60)
    print("  FlowForge AI - Phase 1 POC Tests")
    print("="*60)
    
    results = []
    
    # 1. Health
    results.append(test_health())
    
    # 2. Seed
    results.append(test_seed())
    
    # 3. Create workflow
    success, workflow_id = test_create_workflow()
    results.append(success)
    
    if not workflow_id:
        print("\n❌ Cannot continue without workflow_id")
        return
    
    # 4. Validate
    results.append(test_validate_workflow(workflow_id))
    
    # 5. Publish
    success, version_id = test_publish_workflow(workflow_id)
    results.append(success)
    
    if not version_id:
        print("\n❌ Cannot continue without version_id")
        return
    
    # ═══════════════════════════════════════════════
    # Test Case A: Short leave (≤3 days) → Manager approval only
    # ═══════════════════════════════════════════════
    print("\n" + "="*60)
    print("  TEST CASE A: Short Leave (2 days) → Manager Path")
    print("="*60)
    
    success, run_id_a = test_start_run(version_id, days_requested=2)
    results.append(success)
    
    if run_id_a:
        # Should create a form task first
        test_get_run(run_id_a)
        results.append(test_complete_task(run_id_a))
        
        # After form completion, condition evaluates → manager approval
        test_get_run(run_id_a)
        results.append(test_approve(run_id_a, "manager"))
        
        # Should complete
        run_data = test_get_run(run_id_a)
        final_status = run_data.get("run", {}).get("status")
        results.append(print_result("Run A Final Status", final_status == "completed", f"Status: {final_status}"))
        
        results.append(test_audit_trail(run_id_a))
    
    # ═══════════════════════════════════════════════
    # Test Case B: Long leave (>3 days) → HR then Manager approval
    # ═══════════════════════════════════════════════
    print("\n" + "="*60)
    print("  TEST CASE B: Long Leave (5 days) → HR + Manager Path")
    print("="*60)
    
    success, run_id_b = test_start_run(version_id, days_requested=5)
    results.append(success)
    
    if run_id_b:
        test_get_run(run_id_b)
        results.append(test_complete_task(run_id_b))
        
        # After form, condition → HR approval first
        test_get_run(run_id_b)
        results.append(test_approve(run_id_b, "hr_admin"))
        
        # Then manager approval
        test_get_run(run_id_b)
        results.append(test_approve(run_id_b, "manager"))
        
        # Should complete
        run_data = test_get_run(run_id_b)
        final_status = run_data.get("run", {}).get("status")
        results.append(print_result("Run B Final Status", final_status == "completed", f"Status: {final_status}"))
        
        results.append(test_audit_trail(run_id_b))
    
    # ═══════════════════════════════════════════════
    # Test Case C: Rejection path
    # ═══════════════════════════════════════════════
    print("\n" + "="*60)
    print("  TEST CASE C: Rejection Path")
    print("="*60)
    
    success, run_id_c = test_start_run(version_id, days_requested=2)
    results.append(success)
    
    if run_id_c:
        test_get_run(run_id_c)
        results.append(test_complete_task(run_id_c))
        
        test_get_run(run_id_c)
        results.append(test_reject(run_id_c, "manager"))
        
        run_data = test_get_run(run_id_c)
        final_status = run_data.get("run", {}).get("status")
        results.append(print_result("Run C Final Status (Rejected)", final_status == "completed", f"Status: {final_status}"))
    
    # ═══════════════════════════════════════════════
    # Test GPT-4o
    # ═══════════════════════════════════════════════
    print("\n" + "="*60)
    print("  TEST: GPT-4o AI Assistance")
    print("="*60)
    results.append(test_gpt4o())
    
    # Summary
    print("\n" + "="*60)
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"  RESULTS: {passed}/{total} tests passed")
    if passed == total:
        print("  🎉 ALL TESTS PASSED - Core workflow engine is working!")
    else:
        print(f"  ⚠️  {total - passed} tests failed")
    print("="*60)

if __name__ == "__main__":
    run_all_tests()
