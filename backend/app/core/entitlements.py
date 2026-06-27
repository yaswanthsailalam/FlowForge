from typing import List, Optional
from backend.app.db.mongodb import db

def get_client_entitlements(client_id: str) -> dict:
    entitlements = {
        "products": set(),
        "modules": set(),
        "features": set(),
        "limits": {}
    }
    client = db["client_organisations"].find_one({"organisation_id": client_id})
    if not client:
        return entitlements
    plan_id = client.get("plan_id")
    if plan_id:
        plan = db["plans"].find_one({"plan_id": plan_id})
        if plan:
            entitlements["products"].update(plan.get("included_product_ids", []))
            entitlements["modules"].update(plan.get("included_module_ids", []))
            entitlements["features"].update(plan.get("included_feature_keys", []))
            entitlements["limits"].update(plan.get("limits", {}))
    overrides = db["client_entitlements"].find({"client_id": client_id, "is_enabled": True})
    for ov in overrides:
        target_type = ov["target_type"]
        target_id = ov["target_id"]
        if target_type == "product":
            entitlements["products"].add(target_id)
        elif target_type == "module":
            entitlements["modules"].add(target_id)
        elif target_type == "feature":
            entitlements["features"].add(target_id)
        entitlements["limits"].update(ov.get("limits_override", {}))
    entitlements["products"] = list(entitlements["products"])
    entitlements["modules"] = list(entitlements["modules"])
    entitlements["features"] = list(entitlements["features"])
    return entitlements

def check_feature_access(client_id: str, feature_key: str) -> bool:
    entitlements = get_client_entitlements(client_id)
    return feature_key in entitlements["features"]
