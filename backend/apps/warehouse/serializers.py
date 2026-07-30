from rest_framework import serializers


class DashboardSummarySerializer(serializers.Serializer):
    total_claims = serializers.IntegerField()
    total_billed = serializers.FloatField()
    total_paid = serializers.FloatField()
    avg_paid_amount = serializers.FloatField()
    denial_rate = serializers.FloatField()
    top_denial_reason = serializers.CharField(allow_null=True)
    open_data_quality_issues = serializers.IntegerField()
    recent_audit_events = serializers.ListField()
    compliance_status = serializers.DictField()
    monthly_trend = serializers.ListField()
    synthetic_data_notice = serializers.CharField()


class ClaimListItemSerializer(serializers.Serializer):
    claim_id = serializers.CharField()
    claim_status = serializers.CharField()
    claim_type = serializers.CharField()
    service_date_start = serializers.DateField()
    service_date_end = serializers.DateField()
    billed_amount = serializers.FloatField()
    paid_amount = serializers.FloatField()
    provider_name = serializers.CharField()
    payer_name = serializers.CharField()
    denial_reason = serializers.CharField(allow_null=True)


class ClaimServiceLineSerializer(serializers.Serializer):
    line_number = serializers.IntegerField()
    procedure_category_name = serializers.CharField(allow_null=True)
    units = serializers.IntegerField()
    billed_amount = serializers.FloatField()
    allowed_amount = serializers.FloatField()
    paid_amount = serializers.FloatField()


class ClaimDetailSerializer(ClaimListItemSerializer):
    member_id = serializers.CharField()
    diagnosis_category_name = serializers.CharField(allow_null=True)
    submitted_date = serializers.DateField()
    service_lines = ClaimServiceLineSerializer(many=True)


class DataQualityResultSerializer(serializers.Serializer):
    check_name = serializers.CharField()
    table_name = serializers.CharField()
    severity = serializers.CharField()
    status = serializers.CharField()
    failed_count = serializers.IntegerField()
    sample_record_key = serializers.CharField(allow_null=True)
    message = serializers.CharField()
    created_at = serializers.DateTimeField()


class DataQualityScorecardSerializer(serializers.Serializer):
    table_name = serializers.CharField()
    total_checks = serializers.IntegerField()
    passed_checks = serializers.IntegerField()
    failed_checks = serializers.IntegerField()
    quality_score = serializers.FloatField()
    last_run_at = serializers.DateTimeField(allow_null=True)


class ExportRequestSerializer(serializers.Serializer):
    export_type = serializers.ChoiceField(
        choices=["aggregate_claims", "masked_claims", "data_quality_report", "audit_report"]
    )
    reason = serializers.CharField(max_length=255)
