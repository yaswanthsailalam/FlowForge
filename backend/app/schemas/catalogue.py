from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# --- Industry ---
class IndustryBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "active"
    source_type: str = "global"  # global, workspace
    visibility: str = "public"  # public, private

class IndustryCreate(IndustryBase):
    pass

class IndustryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    visibility: Optional[str] = None

class IndustryInDB(IndustryBase):
    industry_id: str
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None

# --- Business Segment ---
class BusinessSegmentBase(BaseModel):
    name: str
    description: Optional[str] = None
    industry_ids: List[str] = []
    status: str = "active"
    source_type: str = "global"
    visibility: str = "public"
    workspace_id: Optional[str] = None

class BusinessSegmentCreate(BusinessSegmentBase):
    pass

class BusinessSegmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    industry_ids: Optional[List[str]] = None
    status: Optional[str] = None
    visibility: Optional[str] = None

class BusinessSegmentInDB(BusinessSegmentBase):
    segment_id: str
    created_at: datetime
    updated_at: datetime

# --- Department ---
class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None
    workspace_id: str
    status: str = "active"
    owner_role: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    owner_role: Optional[str] = None

class DepartmentInDB(DepartmentBase):
    department_id: str
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None

# --- Team ---
class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None
    workspace_id: str
    department_id: Optional[str] = None
    team_type: str = "functional"  # functional, cross-functional
    status: str = "active"

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    department_id: Optional[str] = None
    team_type: Optional[str] = None
    status: Optional[str] = None

class TeamInDB(TeamBase):
    team_id: str
    created_at: datetime
    updated_at: datetime

# --- Process Family ---
class ProcessFamilyBase(BaseModel):
    name: str
    description: Optional[str] = None
    industry_ids: List[str] = []
    department_ids: List[str] = []
    team_ids: List[str] = []
    source_type: str = "global"
    workspace_id: Optional[str] = None
    status: str = "active"
    tags: List[str] = []

class ProcessFamilyCreate(ProcessFamilyBase):
    pass

class ProcessFamilyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    industry_ids: Optional[List[str]] = None
    department_ids: Optional[List[str]] = None
    team_ids: Optional[List[str]] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None

class ProcessFamilyInDB(ProcessFamilyBase):
    family_id: str
    created_at: datetime
    updated_at: datetime

# --- Business Process Model ---
class ProcessModelBase(BaseModel):
    name: str
    description: str
    purpose: Optional[str] = None
    source_type: str = "global"
    workspace_id: Optional[str] = None
    ownership_scope: str = "global"  # global, workspace
    catalogue_status: str = "draft"  # draft, in_review, published, deprecated, archived
    publication_status: str = "draft"
    version: str = "1.0"
    applicable_industries: List[str] = []
    applicable_segments: List[str] = []
    applicable_departments: List[str] = []
    applicable_teams: List[str] = []
    applicable_families: List[str] = []
    tags: List[str] = []
    expected_stages: List[Dict[str, Any]] = []
    supported_step_types: List[str] = []
    suggested_roles: List[str] = []
    approval_points: List[str] = []
    decision_paths: List[Dict[str, Any]] = []
    required_config_areas: List[str] = []
    supported_input_types: List[str] = []
    expected_output_types: List[str] = []
    exception_categories: List[str] = []
    completion_conditions: List[str] = []
    validation_rules: List[Dict[str, Any]] = []
    model_owner: Optional[str] = None
    parent_model_id: Optional[str] = None
    replacement_model_id: Optional[str] = None
    visibility_rules: Dict[str, Any] = {}
    deprecated: bool = False

class ProcessModelCreate(ProcessModelBase):
    pass

class ProcessModelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    purpose: Optional[str] = None
    catalogue_status: Optional[str] = None
    publication_status: Optional[str] = None
    version: Optional[str] = None
    applicable_industries: Optional[List[str]] = None
    applicable_segments: Optional[List[str]] = None
    applicable_departments: Optional[List[str]] = None
    applicable_teams: Optional[List[str]] = None
    applicable_families: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    expected_stages: Optional[List[Dict[str, Any]]] = None
    supported_step_types: Optional[List[str]] = None
    suggested_roles: Optional[List[str]] = None
    approval_points: Optional[List[str]] = None
    decision_paths: Optional[List[Dict[str, Any]]] = None
    required_config_areas: Optional[List[str]] = None
    supported_input_types: Optional[List[str]] = None
    expected_output_types: Optional[List[str]] = None
    exception_categories: Optional[List[str]] = None
    completion_conditions: Optional[List[str]] = None
    validation_rules: Optional[List[Dict[str, Any]]] = None
    model_owner: Optional[str] = None
    replacement_model_id: Optional[str] = None
    visibility_rules: Optional[Dict[str, Any]] = None
    deprecated: Optional[bool] = None

class ProcessModelInDB(ProcessModelBase):
    model_id: str
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None

# --- Process Model Variant ---
class ModelVariantBase(BaseModel):
    model_id: str
    name: str
    description: Optional[str] = None
    applicability: Dict[str, Any] = {}
    configuration_overrides: Dict[str, Any] = {}
    additional_stages: List[Dict[str, Any]] = []
    removed_optional_stages: List[str] = []
    modified_validation_rules: List[Dict[str, Any]] = []
    modified_role_suggestions: List[str] = []
    modified_input_requirements: List[Dict[str, Any]] = []
    version: str = "1.0"
    status: str = "active"
    workspace_id: Optional[str] = None

class ModelVariantCreate(ModelVariantBase):
    pass

class ModelVariantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    applicability: Optional[Dict[str, Any]] = None
    configuration_overrides: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    version: Optional[str] = None

class ModelVariantInDB(ModelVariantBase):
    variant_id: str
    created_at: datetime
    updated_at: datetime

# --- Workflow Template ---
class WorkflowTemplateBase(BaseModel):
    process_model_id: str
    variant_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    applicability_metadata: Dict[str, Any] = {}
    trigger_info: Dict[str, Any] = {}
    stages: List[Dict[str, Any]] = []
    steps: List[Dict[str, Any]] = []
    supported_roles: List[str] = []
    input_definitions: List[Dict[str, Any]] = []
    output_definitions: List[Dict[str, Any]] = []
    approval_placeholders: List[Dict[str, Any]] = []
    condition_placeholders: List[Dict[str, Any]] = []
    notification_placeholders: List[Dict[str, Any]] = []
    integration_placeholders: List[Dict[str, Any]] = []
    exception_paths: List[Dict[str, Any]] = []
    completion_paths: List[Dict[str, Any]] = []
    validation_requirements: List[Dict[str, Any]] = []
    publication_status: str = "draft"
    version: str = "1.0"
    source_type: str = "global"
    workspace_id: Optional[str] = None

class WorkflowTemplateCreate(WorkflowTemplateBase):
    pass

class WorkflowTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    publication_status: Optional[str] = None
    version: Optional[str] = None

class WorkflowTemplateInDB(WorkflowTemplateBase):
    template_id: str
    created_at: datetime
    updated_at: datetime

# --- Catalogue Favourites ---
class CatalogueFavourite(BaseModel):
    user_id: str
    workspace_id: str
    model_id: str
    created_at: datetime

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
