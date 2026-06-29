from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    status: str = "active"
    version: str = "1.0.0"
    release_notes: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductInDB(ProductBase):
    product_id: str
    created_at: datetime
    updated_at: datetime

class ModuleBase(BaseModel):
    product_id: str
    name: str
    slug: str
    description: Optional[str] = None
    status: str = "active"

class ModuleCreate(ModuleBase):
    pass

class ModuleInDB(ModuleBase):
    module_id: str
    created_at: datetime
    updated_at: datetime

class FeatureBase(BaseModel):
    module_id: str
    key: str
    name: str
    description: Optional[str] = None
    status: str = "active"
    config_schema: Optional[Dict[str, Any]] = None

class FeatureCreate(FeatureBase):
    pass

class FeatureInDB(FeatureBase):
    feature_id: str
    created_at: datetime
    updated_at: datetime

class PlanBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    status: str = "active"
    included_product_ids: List[str] = []
    included_module_ids: List[str] = []
    included_feature_keys: List[str] = []
    limits: Dict[str, Any] = {}
    is_trial_available: bool = True
    version: str = "1.0"

class PlanCreate(PlanBase):
    pass

class PlanInDB(PlanBase):
    plan_id: str
    created_at: datetime
    updated_at: datetime

class ClientEntitlementBase(BaseModel):
    client_id: str
    target_type: str
    target_id: str
    source_plan_id: Optional[str] = None
    is_enabled: bool = True
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    limits_override: Dict[str, Any] = {}
    reason: Optional[str] = None

class ClientEntitlementCreate(ClientEntitlementBase):
    pass

class ClientEntitlementInDB(ClientEntitlementBase):
    entitlement_id: str
    created_at: datetime
    updated_at: datetime
    created_by: str
