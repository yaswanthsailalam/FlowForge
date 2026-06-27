from typing import List, Dict, Any
from backend.app.schemas.catalogue import ProcessModelInDB, ExtensionPolicy

class ExtensionPolicyViolation(Exception):
    def __init__(self, message: str, violations: List[str]):
        self.message = message
        self.violations = violations

def validate_variant_against_policy(source_model: dict, variant_data: Dict[str, Any]):
    """
    Validates a proposed variant against the source model's extension policy.
    Accepts source_model as a dict (from MongoDB).
    """
    policy_dict = source_model.get("extension_policy", {})
    # Convert to object for easier access if needed or just use dict.get()
    policy = ExtensionPolicy(**policy_dict)

    violations = []

    # 1. Identity Overrides
    if not policy.allow_name_override and variant_data.get("name") != source_model.get("name"):
        violations.append("Overriding model name is prohibited.")
    if not policy.allow_description_override and variant_data.get("description") != source_model.get("description"):
        violations.append("Overriding model description is prohibited.")
    if not policy.allow_purpose_override and variant_data.get("business_purpose") != source_model.get("business_purpose"):
        violations.append("Overriding business purpose is prohibited.")

    # 2. Stage Validations
    source_stages = {s["stage_id"]: s for s in source_model.get("stages", [])}
    variant_stages = variant_data.get("stages", [])
    variant_stage_ids = [s.get("stage_id") for s in variant_stages if s.get("stage_id")]

    for stage_id in policy.locked_mandatory_stages:
        if stage_id not in variant_stage_ids:
            violations.append(f"Locked mandatory stage '{source_stages[stage_id]['name']}' was removed.")

    if not policy.allow_optional_stage_removal:
        source_stage_ids = set(source_stages.keys())
        removed_stages = source_stage_ids - set(variant_stage_ids)
        if removed_stages:
            violations.append("Removal of optional stages is prohibited by policy.")

    if not policy.allow_additional_stages:
        new_stages = [s for s in variant_stages if s.get("stage_id") not in source_stages]
        if new_stages:
            violations.append("Adding new stages is prohibited by policy.")

    if not policy.allow_stage_reordering:
        common_ids = [s["stage_id"] for s in source_model.get("stages", []) if s["stage_id"] in variant_stage_ids]
        variant_common_ids = [s["stage_id"] for s in variant_stages if s["stage_id"] in source_stages]
        if common_ids != variant_common_ids:
            violations.append("Reordering inherited stages is prohibited.")

    # 3. Activity Validations
    if not policy.allow_additional_activities:
        for v_stage in variant_stages:
            s_stage = source_stages.get(v_stage.get("stage_id"))
            if s_stage:
                s_act_ids = {a["activity_id"] for s in source_model.get("stages", []) for a in s.get("activities", [])}
                v_act_ids = {a.get("activity_id") for a in v_stage.get("activities", []) if a.get("activity_id")}
                if v_act_ids - s_act_ids:
                    violations.append(f"Adding activities to stage '{v_stage['name']}' is prohibited.")

    # 4. Input Validations
    source_input_keys = {i["key"] for i in source_model.get("inputs", [])}
    variant_inputs = variant_data.get("inputs", [])
    variant_input_keys = {i.get("key") for i in variant_inputs}

    for key in policy.locked_required_inputs:
        if key not in variant_input_keys:
            violations.append(f"Locked required input '{key}' was removed.")

    if not policy.allow_input_additions:
        new_inputs = variant_input_keys - source_input_keys
        if new_inputs:
            violations.append("Adding new inputs is prohibited by policy.")

    # 5. Role Validations
    if not policy.allow_role_overrides:
        s_roles = {r["role_name"] for r in source_model.get("participant_roles", [])}
        v_roles = {r.get("role_name") for r in variant_data.get("participant_roles", [])}
        if s_roles != v_roles:
            violations.append("Modifying participant roles is prohibited.")

    if violations:
        raise ExtensionPolicyViolation("Extension policy validation failed", violations)

    return True
