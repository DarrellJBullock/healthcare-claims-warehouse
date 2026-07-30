"""
Audit logging service.

Synthetic data only -- ip_address_placeholder is always a demo value, never
a real client IP, since this project never handles real PHI/ePHI traffic.
"""

from apps.compliance.models import AuditEvent


def log_event(
    *,
    user_role: str,
    action: str,
    user_id: str = "demo-user",
    resource_type: str = "",
    resource_id: str = "",
    reason: str = "",
    status: str = "SUCCESS",
) -> AuditEvent:
    return AuditEvent.objects.create(
        user_id=user_id,
        user_role=user_role,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        reason=reason,
        status=status,
        ip_address_placeholder="0.0.0.0",
    )


def log_access_denied(*, user_role: str, resource_type: str, resource_id: str = "", reason: str = "") -> AuditEvent:
    return log_event(
        user_role=user_role,
        action="ACCESS_DENIED",
        resource_type=resource_type,
        resource_id=resource_id,
        reason=reason,
        status="DENIED",
    )
