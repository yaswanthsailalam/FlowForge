from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from backend.app.api import deps
from backend.app.core.utils import utcnow, new_id, serialize_doc
from backend.app.db.mongodb import db
from backend.app.schemas.product import (
    ProductCreate, ProductInDB,
    ModuleCreate, ModuleInDB,
    FeatureCreate, FeatureInDB,
    PlanCreate, PlanInDB,
    ClientEntitlementCreate, ClientEntitlementInDB
)
from backend.app.core.entitlements import check_feature_access

router = APIRouter()

products_col = db["products"]
modules_col = db["modules"]
features_col = db["features"]
plans_col = db["plans"]
entitlements_col = db["client_entitlements"]

# --- Entitlement Enforcement Logic ---
def verify_entitlement(feature_key: str):
    def entitlement_checker(context: dict = Depends(deps.get_workspace_context)):
        workspace = context.get("workspace")
        if not workspace:
             raise HTTPException(status_code=400, detail="Workspace context required")

        org_id = workspace.get("organisation_id")
        if not org_id:
             # Backward compatibility: for now allow if no org_id linked
             return context

        if not check_feature_access(org_id, feature_key):
             raise HTTPException(
                 status_code=status.HTTP_403_FORBIDDEN,
                 detail=f"Organisation lacks entitlement for feature: {feature_key}"
             )
        return context
    return entitlement_checker

@router.post("/products", response_model=ProductInDB)
def create_product(
    product_in: ProductCreate,
    current_user: Any = Depends(deps.require_platform_role(["platform_owner", "platform_product_admin"]))
):
    product = product_in.model_dump()
    product["product_id"] = new_id()
    product["created_at"] = utcnow()
    product["updated_at"] = utcnow()
    products_col.insert_one(product)
    return serialize_doc(product)

@router.get("/products", response_model=List[ProductInDB])
def list_products(
    current_user: Any = Depends(deps.get_current_user)
):
    return serialize_doc(list(products_col.find()))

@router.post("/modules", response_model=ModuleInDB)
def create_module(
    module_in: ModuleCreate,
    current_user: Any = Depends(deps.require_platform_role(["platform_owner", "platform_product_admin"]))
):
    module = module_in.model_dump()
    module["module_id"] = new_id()
    module["created_at"] = utcnow()
    module["updated_at"] = utcnow()
    modules_col.insert_one(module)
    return serialize_doc(module)

@router.post("/features", response_model=FeatureInDB)
def create_feature(
    feature_in: FeatureCreate,
    current_user: Any = Depends(deps.require_platform_role(["platform_owner", "platform_product_admin"]))
):
    feature = feature_in.model_dump()
    feature["feature_id"] = new_id()
    feature["created_at"] = utcnow()
    feature["updated_at"] = utcnow()
    features_col.insert_one(feature)
    return serialize_doc(feature)

@router.post("/plans", response_model=PlanInDB)
def create_plan(
    plan_in: PlanCreate,
    current_user: Any = Depends(deps.require_platform_role(["platform_owner", "platform_product_admin"]))
):
    plan = plan_in.model_dump()
    plan["plan_id"] = new_id()
    plan["created_at"] = utcnow()
    plan["updated_at"] = utcnow()
    plans_col.insert_one(plan)
    return serialize_doc(plan)

@router.get("/plans", response_model=List[PlanInDB])
def list_plans(
    current_user: Any = Depends(deps.get_current_user)
):
    return serialize_doc(list(plans_col.find()))

@router.post("/clients/{client_id}/entitlements", response_model=ClientEntitlementInDB)
def create_client_entitlement(
    client_id: str,
    entitlement_in: ClientEntitlementCreate,
    current_user: Any = Depends(deps.require_platform_role(["platform_owner", "platform_client_success_admin"]))
):
    entitlement = entitlement_in.model_dump()
    entitlement["entitlement_id"] = new_id()
    entitlement["client_id"] = client_id
    entitlement["created_by"] = current_user.user_id
    entitlement["created_at"] = utcnow()
    entitlement["updated_at"] = utcnow()
    entitlements_col.insert_one(entitlement)
    return serialize_doc(entitlement)

@router.get("/clients/{client_id}/entitlements", response_model=List[ClientEntitlementInDB])
def list_client_entitlements(
    client_id: str,
    current_user: Any = Depends(deps.get_current_user)
):
    return serialize_doc(list(entitlements_col.find({"client_id": client_id})))
