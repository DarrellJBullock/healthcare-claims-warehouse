"""
Role-based access control for the demo warehouse dashboard.

There is no real authentication in this portfolio project -- the frontend's
RoleSwitcher sends the selected role via the X-Demo-Role header, and this
service decides what that role is allowed to see or export ("minimum
necessary" access, HIPAA-aware pattern).
"""

DEMO_ROLES = ["Admin", "Data Engineer", "Claims Analyst", "Manager", "Auditor", "Read Only"]

DEFAULT_ROLE = "Read Only"

EXPORT_TYPES = {
    "aggregate_claims": {"Admin", "Manager", "Data Engineer", "Claims Analyst", "Auditor"},
    "masked_claims": {"Admin", "Claims Analyst"},
    "data_quality_report": {"Admin", "Data Engineer"},
    "audit_report": {"Admin", "Auditor"},
}


def normalize_role(role: str) -> str:
    return role if role in DEMO_ROLES else DEFAULT_ROLE


def get_permissions(role: str) -> dict:
    role = normalize_role(role)
    return {
        "role": role,
        "can_view_row_level_claims": role in {"Admin", "Claims Analyst", "Data Engineer"},
        "can_view_member_detail": role in {"Admin", "Claims Analyst"},
        "can_view_aggregate_only": role in {"Manager", "Read Only"},
        "can_view_data_quality": role in {"Admin", "Data Engineer"},
        "can_view_compliance": role in {"Admin", "Auditor"},
        "can_view_audit_log": role in {"Admin", "Auditor"},
        "can_run_quality_checks": role in {"Admin", "Data Engineer"},
        "can_export": role in {"Admin", "Manager", "Data Engineer", "Claims Analyst", "Auditor"},
        "can_manage_role_controls": role == "Admin",
        # Only Admin sees fully unmasked identifiers; every other role is
        # "minimum necessary" and gets masked identifiers.
        "mask_identifiers": role != "Admin",
    }


def can_export(role: str, export_type: str) -> bool:
    role = normalize_role(role)
    allowed_roles = EXPORT_TYPES.get(export_type, set())
    return role in allowed_roles


def role_from_request(request) -> str:
    return normalize_role(request.headers.get("X-Demo-Role", DEFAULT_ROLE))
