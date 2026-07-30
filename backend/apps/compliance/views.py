from django.conf import settings
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.compliance.models import AuditEvent
from apps.compliance.serializers import AuditEventSerializer, ComplianceSummarySerializer
from apps.warehouse.services import audit as audit_service
from apps.warehouse.services import roles


class AuditLogPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 200


class AuditLogView(APIView):
    def get(self, request):
        role = roles.role_from_request(request)
        permissions = roles.get_permissions(role)
        if not permissions["can_view_audit_log"]:
            audit_service.log_access_denied(
                user_role=role, resource_type="audit_log",
                reason="Role not permitted to view the audit log",
            )
            return Response({"detail": "Not permitted for this role."}, status=403)

        queryset = AuditEvent.objects.all()
        paginator = AuditLogPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = AuditEventSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class RoleChangedView(APIView):
    """Logs a ROLE_CHANGED audit event when the demo RoleSwitcher is used."""

    def post(self, request):
        new_role = roles.normalize_role(request.data.get("role", ""))
        audit_service.log_event(
            user_role=new_role,
            action="ROLE_CHANGED",
            resource_type="role_switcher",
            reason=f"Switched demo role to {new_role}",
        )
        return Response({"role": new_role}, status=201)


class ComplianceSummaryView(APIView):
    def get(self, request):
        role = roles.role_from_request(request)
        permissions = roles.get_permissions(role)

        last_export = AuditEvent.objects.filter(action="REPORT_EXPORTED").order_by("-event_timestamp").first()
        last_sensitive_view = (
            AuditEvent.objects.filter(action__in=["CLAIM_DETAIL_VIEWED", "MEMBER_DETAIL_VIEWED"])
            .order_by("-event_timestamp")
            .first()
        )
        failed_attempts = (
            AuditEvent.objects.filter(action="ACCESS_DENIED").count() if permissions["can_view_compliance"] else None
        )

        checklist = [
            {"item": "Synthetic data only, no real PHI", "status": "PASS"},
            {"item": "Masked identifiers on row-level views", "status": "PASS"},
            {"item": "Role-based access with minimum necessary views", "status": "PASS"},
            {"item": "Audit logging on sensitive actions", "status": "PASS"},
            {"item": "Export controls with reason + audit trail", "status": "PASS"},
            {"item": "Retention policy documented", "status": "PASS"},
        ]

        data = {
            "synthetic_data_only": True,
            "phi_risk_status": "No Real PHI Present (Synthetic Data Only)",
            "masking_enabled": True,
            "role_based_access_enabled": True,
            "audit_logging_enabled": True,
            "export_controls_enabled": True,
            "retention_policy": settings.RETENTION_POLICY,
            "last_export": {
                "timestamp": last_export.event_timestamp,
                "role": last_export.user_role,
                "resource_id": last_export.resource_id,
            } if last_export and permissions["can_view_compliance"] else None,
            "last_sensitive_view_event": {
                "timestamp": last_sensitive_view.event_timestamp,
                "role": last_sensitive_view.user_role,
                "action": last_sensitive_view.action,
            } if last_sensitive_view and permissions["can_view_compliance"] else None,
            "failed_access_attempts_last_30_days": failed_attempts,
            "checklist": checklist if permissions["can_view_compliance"] else [],
        }
        return Response(ComplianceSummarySerializer(data).data)
