"""
SQL-first pipeline runner: applies staging views, builds warehouse
dimensions/facts, and rebuilds analytics marts by executing the .sql files
in backend/sql/ in dependency order.
"""

from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import connection

SQL_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent / "sql"

# Execution order matters: staging depends on raw, warehouse depends on
# staging, marts depend on warehouse (+ audit/compliance for two marts),
# indexes go last.
BUILD_STEPS = [
    ("staging", "001_staging_views.sql"),
    ("warehouse", "001_dimensions.sql"),
    ("warehouse", "002_facts.sql"),
    ("marts", "001_claims_summary.sql"),
    ("marts", "002_denial_trends.sql"),
    ("marts", "003_provider_performance.sql"),
    ("marts", "004_payer_performance.sql"),
    ("marts", "005_member_utilization.sql"),
    ("marts", "006_payment_reconciliation.sql"),
    ("marts", "007_monthly_claims_kpis.sql"),
    ("marts", "008_data_quality_scorecard.sql"),
    ("marts", "009_compliance_audit_summary.sql"),
    ("indexes", "001_indexes.sql"),
]


class Command(BaseCommand):
    help = "Builds staging views, warehouse dims/facts, and analytics marts from backend/sql/*"

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            for folder, filename in BUILD_STEPS:
                sql_path = SQL_ROOT / folder / filename
                self.stdout.write(f"Applying {folder}/{filename}...")
                cursor.execute(sql_path.read_text())
        self.stdout.write(self.style.SUCCESS("Warehouse dimensions, facts, and marts rebuilt."))
