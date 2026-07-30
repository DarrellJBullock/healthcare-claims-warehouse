"""
Resets the warehouse to an empty state: truncates raw synthetic data,
warehouse dimensions/facts, marts, and data quality results.

The audit trail (audit.audit_events) is intentionally NOT truncated -- per
the retention policy demo, audit logs are treated as retained for 6 years
and are not cleared by a routine warehouse reset.
"""

from django.core.management.base import BaseCommand
from django.db import connection

from apps.warehouse.services import audit as audit_service

RAW_TABLES = [
    "raw.raw_adjustments",
    "raw.raw_payments",
    "raw.raw_claim_service_lines",
    "raw.raw_claims",
    "raw.raw_eligibility",
    "raw.raw_members",
    "raw.raw_providers",
    "raw.raw_payers",
    "raw.raw_denial_codes",
    "raw.raw_diagnosis_categories",
    "raw.raw_procedure_categories",
]

WAREHOUSE_AND_MART_TABLES = [
    "warehouse.fact_eligibility_coverage",
    "warehouse.fact_adjustment",
    "warehouse.fact_payment",
    "warehouse.fact_claim_service_line",
    "warehouse.fact_claim",
    "warehouse.dim_member",
    "warehouse.dim_provider",
    "warehouse.dim_payer",
    "warehouse.dim_diagnosis_category",
    "warehouse.dim_procedure_category",
    "warehouse.dim_denial_reason",
    "marts.mart_claims_summary",
    "marts.mart_denial_trends",
    "marts.mart_provider_performance",
    "marts.mart_payer_performance",
    "marts.mart_member_utilization",
    "marts.mart_payment_reconciliation",
    "marts.mart_monthly_claims_kpis",
    "marts.mart_data_quality_scorecard",
    "marts.mart_compliance_audit_summary",
    "compliance.data_quality_results",
]


class Command(BaseCommand):
    help = "Truncates raw, warehouse, and mart tables for a clean re-seed (audit log is preserved)."

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            for table in WAREHOUSE_AND_MART_TABLES:
                cursor.execute(f"TRUNCATE TABLE {table} CASCADE;")
            for table in RAW_TABLES:
                cursor.execute(f"TRUNCATE TABLE {table} CASCADE;")

        audit_service.log_event(
            user_role="Admin",
            action="RETENTION_JOB_RAN",
            resource_type="warehouse",
            reason="Manual reset_warehouse command executed (raw/warehouse/marts truncated, audit log preserved)",
        )
        self.stdout.write(self.style.SUCCESS("Warehouse reset. Run seed_synthetic_claims and build_marts next."))
