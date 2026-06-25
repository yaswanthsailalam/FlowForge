from pymongo import MongoClient, ASCENDING, DESCENDING
from backend.app.core.config import settings

client = MongoClient(settings.MONGO_URL)
db = client[settings.DB_NAME]

# Core Collections
users_col = db["users"]
workspaces_col = db["workspaces"]
workspace_memberships_col = db["workspace_memberships"]

# Workflow Engine Collections (Preserved)
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
roles_col = db["roles"]
permissions_col = db["permissions"]

def init_db():
    # Security/Auth Indexes
    users_col.create_index([("email", ASCENDING)], unique=True)
    users_col.create_index([("user_id", ASCENDING)], unique=True)

    workspaces_col.create_index([("workspace_id", ASCENDING)], unique=True)

    workspace_memberships_col.create_index(
        [("workspace_id", ASCENDING), ("user_id", ASCENDING)],
        unique=True
    )
    workspace_memberships_col.create_index([("user_id", ASCENDING)])

    # Preserved Engine Indexes
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
