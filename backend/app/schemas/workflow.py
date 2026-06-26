from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# --- Trigger ---
class TriggerDefinition(BaseModel):
    trigger_id: str = Field(default_factory=lambda: "trigger-1")
    type: str  # manual, form_submission, scheduled, api, webhook, integration_event, workflow_event
    name: str
    description: Optional[str] = None
    config: Dict[str, Any] = {}
    input_schema: Dict[str, Any] = {}

# --- Input ---
class InputDefinition(BaseModel):
    key: str
    label: str
    description: Optional[str] = None
    data_type: str  # string, number, boolean, date, object, array
    required: bool = True
    validation_rules: Dict[str, Any] = {}
    allowed_values: List[Any] = []
    default_value: Optional[Any] = None
    sensitivity: str = "internal"  # public, internal, confidential, highly_confidential
    visibility: str = "visible"  # visible, hidden, read_only
    editable: bool = True

# --- Document ---
class DocumentRequirement(BaseModel):
    name: str
    description: Optional[str] = None
    required: bool = True
    allowed_types: List[str] = []
    max_size_mb: Optional[int] = None
    verification_required: bool = False
    verification_role: Optional[str] = None

# --- Stage ---
class StageDefinition(BaseModel):
    stage_id: str
    name: str
    description: Optional[str] = None
    sequence: int
    is_optional: bool = False

# --- Step ---
class StepDefinition(BaseModel):
    step_id: str
    name: str
    description: Optional[str] = None
    step_type: str
    stage_id: Optional[str] = None
    assigned_role: Optional[str] = None
    config: Dict[str, Any] = {}
    transitions: Dict[str, str] = {}  # e.g., {"success": "step_2", "failure": "step_error"}
    retry_settings: Dict[str, Any] = {}
    timeout_settings: Dict[str, Any] = {}

# --- Participant ---
class ParticipantDefinition(BaseModel):
    role: str
    name: Optional[str] = None
    department_id: Optional[str] = None
    team_id: Optional[str] = None
    assignment_method: str = "role"  # role, individual, department_head, team_lead
    fallback_role: Optional[str] = None
    description: Optional[str] = None

# --- Approval ---
class ApprovalDefinition(BaseModel):
    approval_id: str
    name: str
    description: Optional[str] = None
    approver_role: str
    department_id: Optional[str] = None
    team_id: Optional[str] = None
    assignment_method: str = "role"
    required_inputs: List[str] = []
    required_documents: List[str] = []
    outcomes: List[str] = ["approved", "rejected"]
    comment_required: bool = False

# --- Notification ---
class NotificationPlaceholder(BaseModel):
    notification_id: str
    name: str
    trigger_event: str
    recipient_role: str
    recipient_department: Optional[str] = None
    recipient_team: Optional[str] = None
    title_template: str
    message_template: str
    delivery_channel: str = "placeholder"

# --- Exception and Completion ---
class WorkflowCompletion(BaseModel):
    valid_states: List[str] = ["completed"]
    required_outputs: List[str] = []
    cancellation_behaviour: str = "cancel_pending"
    incomplete_data_behaviour: str = "allow_completion"

# --- Validation Result ---
class ValidationIssue(BaseModel):
    severity: str  # critical, warning, info
    category: str
    section: str
    field: Optional[str] = None
    stage_id: Optional[str] = None
    step_id: Optional[str] = None
    message: str
    correction: Optional[str] = None

# --- Workflow Draft ---
class WorkflowDefinition(BaseModel):
    trigger: TriggerDefinition
    inputs: List[InputDefinition] = []
    documents: List[DocumentRequirement] = []
    stages: List[StageDefinition] = []
    steps: List[StepDefinition] = []
    participants: List[ParticipantDefinition] = []
    approvals: List[ApprovalDefinition] = []
    notifications: List[NotificationPlaceholder] = []
    completion: WorkflowCompletion = Field(default_factory=WorkflowCompletion)

class WorkflowDraftBase(BaseModel):
    name: str
    description: Optional[str] = None
    owning_department: Optional[str] = None
    participating_departments: List[str] = []
    participating_teams: List[str] = []
    workflow_owner_role: Optional[str] = None
    source_type: str  # model, variant, template, blank
    source_model_id: Optional[str] = None
    source_model_version: Optional[str] = None
    source_variant_id: Optional[str] = None
    source_variant_version: Optional[str] = None
    source_template_id: Optional[str] = None
    source_template_version: Optional[str] = None

class WorkflowDraftCreate(WorkflowDraftBase):
    pass

class WorkflowDraftUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    owning_department: Optional[str] = None
    participating_departments: Optional[List[str]] = None
    participating_teams: Optional[List[str]] = None
    workflow_owner_role: Optional[str] = None
    definition: Optional[WorkflowDefinition] = None
    configuration_complete: Optional[bool] = None

class WorkflowDraftInDB(WorkflowDraftBase):
    workflow_id: str
    workspace_id: str
    status: str = "draft"
    configuration_complete: bool = False
    validation_status: str = "not_validated"
    validation_results: List[ValidationIssue] = []
    unresolved_configuration: List[str] = []
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime
    version: int = 1
    definition: WorkflowDefinition

class WorkflowDraftList(BaseModel):
    workflow_id: str
    name: str
    description: Optional[str] = None
    status: str
    updated_at: datetime
    created_at: datetime
