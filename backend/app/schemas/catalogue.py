from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# --- Extension Policy ---
class ExtensionPolicy(BaseModel):
    allow_name_override: bool = True
    allow_description_override: bool = True
    allow_purpose_override: bool = True
    allow_outcome_additions: bool = True
    allow_additional_stages: bool = True
    allow_optional_stage_removal: bool = True
    allow_stage_reordering: bool = False
    locked_mandatory_stages: List[str] = []
    allow_additional_activities: bool = True
    allow_activity_removal: bool = False
    allow_role_overrides: bool = True
    allow_input_additions: bool = True
    locked_required_inputs: List[str] = []
    allow_document_additions: bool = True
    allow_approval_rule_config: bool = True
    locked_control_points: List[str] = []
    require_internal_review: bool = True

# --- Process Model Blueprint ---
class ProcessModelBase(BaseModel):
    name: str
    description: str
    business_purpose: Optional[str] = None
    purpose: Optional[str] = None
    intended_outcomes: List[str] = []

    industry: Optional[str] = None
    business_segment: Optional[str] = None
    department: Optional[str] = None
    team: Optional[str] = None
    process_family: Optional[str] = None
    tags: List[str] = []

    owner_role: Optional[str] = None
    participant_roles: List[Dict[str, Any]] = []

    stages: List[Dict[str, Any]] = []
    inputs: List[Dict[str, Any]] = []
    documents: List[Dict[str, Any]] = []
    outputs: List[Dict[str, Any]] = []

    decisions: List[Dict[str, Any]] = []
    approvals: List[Dict[str, Any]] = []
    exceptions: List[Dict[str, Any]] = []
    completion_criteria: List[str] = []
    control_points: List[Dict[str, Any]] = []

    source_type: str = "global"
    workspace_id: Optional[str] = None
    parent_model_id: Optional[str] = None
    parent_version: Optional[str] = None

    version: str = "1.0.0"
    lifecycle_status: str = "draft"
    catalogue_status: Optional[str] = None
    is_published: bool = False

    extension_policy: ExtensionPolicy = Field(default_factory=ExtensionPolicy)

    applicable_industries: List[str] = []
    applicable_segments: List[str] = []
    applicable_departments: List[str] = []
    applicable_teams: List[str] = []
    applicable_families: List[str] = []

class ProcessModelCreate(ProcessModelBase):
    pass

class ProcessModelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    business_purpose: Optional[str] = None
    intended_outcomes: Optional[List[str]] = None
    stages: Optional[List[Dict[str, Any]]] = None
    inputs: Optional[List[Dict[str, Any]]] = None
    documents: Optional[List[Dict[str, Any]]] = None
    outputs: Optional[List[Dict[str, Any]]] = None
    lifecycle_status: Optional[str] = None
    catalogue_status: Optional[str] = None
    extension_policy: Optional[ExtensionPolicy] = None

class ProcessModelInDB(ProcessModelBase):
    model_id: str
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None
    created_by: str = "system"

from .catalogue_review import ModelReviewSubmit, ModelReviewDecision, ModelReviewInDB

# --- Pagination ---
class CataloguePagination(BaseModel):
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_prev: bool

class ProcessModelListResponse(BaseModel):
    items: List[ProcessModelInDB]
    pagination: CataloguePagination

# --- Legacy Compatibility ---
class IndustryInDB(BaseModel):
    industry_id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class BusinessSegmentInDB(BaseModel):
    segment_id: str
    name: str
    industry_ids: List[str] = []
    created_at: datetime
    updated_at: datetime

class DepartmentInDB(BaseModel):
    department_id: str
    name: str
    workspace_id: str
    created_at: datetime
    updated_at: datetime

class TeamInDB(BaseModel):
    team_id: str
    name: str
    workspace_id: str
    department_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ProcessFamilyInDB(BaseModel):
    family_id: str
    name: str
    created_at: datetime
    updated_at: datetime

class ModelVariantInDB(BaseModel):
    variant_id: str
    model_id: str
    name: str
    workspace_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class WorkflowTemplateInDB(BaseModel):
    template_id: str
    process_model_id: str
    name: str
    workspace_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
