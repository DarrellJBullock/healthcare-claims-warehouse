from rest_framework import serializers


class ProviderPerformanceSerializer(serializers.Serializer):
    analytics_provider_key = serializers.IntegerField()
    provider_name = serializers.CharField()
    specialty = serializers.CharField()
    network_status = serializers.CharField()
    total_claims = serializers.IntegerField()
    total_billed = serializers.FloatField()
    total_paid = serializers.FloatField()
    denial_rate = serializers.FloatField()
    avg_reimbursement = serializers.FloatField()
    top_procedure_category = serializers.CharField(allow_null=True)
    paid_rank = serializers.IntegerField()
    is_high_risk = serializers.BooleanField()


class PayerPerformanceSerializer(serializers.Serializer):
    analytics_payer_key = serializers.IntegerField()
    payer_name = serializers.CharField()
    payer_type = serializers.CharField()
    total_claims = serializers.IntegerField()
    total_billed = serializers.FloatField()
    total_paid = serializers.FloatField()
    denial_rate = serializers.FloatField()
    avg_days_to_pay = serializers.FloatField(allow_null=True)
    total_adjustments = serializers.FloatField()
    paid_rank = serializers.IntegerField()


class MemberUtilizationSerializer(serializers.Serializer):
    analytics_member_key = serializers.IntegerField()
    plan_type = serializers.CharField()
    gender = serializers.CharField()
    birth_year = serializers.IntegerField()
    claim_count = serializers.IntegerField()
    total_billed = serializers.FloatField()
    total_paid = serializers.FloatField()
    cost_percentile = serializers.IntegerField()
    is_high_cost = serializers.BooleanField()
    coverage_status = serializers.CharField(allow_null=True)


class MemberUtilizationAggregateSerializer(serializers.Serializer):
    plan_type = serializers.CharField()
    member_count = serializers.IntegerField()
    total_claims = serializers.IntegerField()
    total_paid = serializers.FloatField()
    high_cost_members = serializers.IntegerField()
