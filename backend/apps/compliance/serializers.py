from rest_framework import serializers

from apps.compliance.models import AuditEvent


class AuditEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditEvent
        fields = [
            "id", "event_timestamp", "user_id", "user_role", "action",
            "resource_type", "resource_id", "reason", "status", "ip_address_placeholder",
        ]


class ComplianceSummarySerializer(serializers.Serializer):
    synthetic_data_only = serializers.BooleanField()
    phi_risk_status = serializers.CharField()
    masking_enabled = serializers.BooleanField()
    role_based_access_enabled = serializers.BooleanField()
    audit_logging_enabled = serializers.BooleanField()
    export_controls_enabled = serializers.BooleanField()
    retention_policy = serializers.DictField()
    last_export = serializers.DictField(allow_null=True)
    last_sensitive_view_event = serializers.DictField(allow_null=True)
    failed_access_attempts_last_30_days = serializers.IntegerField(allow_null=True)
    checklist = serializers.ListField()
