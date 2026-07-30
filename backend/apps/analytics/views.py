from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.serializers import (
    MemberUtilizationAggregateSerializer,
    MemberUtilizationSerializer,
    PayerPerformanceSerializer,
    ProviderPerformanceSerializer,
)
from apps.warehouse.services import roles
from apps.warehouse.services.db_utils import fetch_all


class ProviderPerformanceView(APIView):
    def get(self, request):
        rows = fetch_all("SELECT * FROM marts.mart_provider_performance ORDER BY paid_rank")
        return Response(ProviderPerformanceSerializer(rows, many=True).data)


class PayerPerformanceView(APIView):
    def get(self, request):
        rows = fetch_all("SELECT * FROM marts.mart_payer_performance ORDER BY paid_rank")
        return Response(PayerPerformanceSerializer(rows, many=True).data)


class MemberUtilizationView(APIView):
    def get(self, request):
        role = roles.role_from_request(request)
        permissions = roles.get_permissions(role)

        if permissions["can_view_aggregate_only"]:
            rows = fetch_all(
                """
                SELECT
                    plan_type,
                    count(*) AS member_count,
                    sum(claim_count) AS total_claims,
                    sum(total_paid) AS total_paid,
                    sum(CASE WHEN is_high_cost THEN 1 ELSE 0 END) AS high_cost_members
                FROM marts.mart_member_utilization
                GROUP BY plan_type
                ORDER BY plan_type
                """
            )
            return Response({"aggregate_only": True, "results": MemberUtilizationAggregateSerializer(rows, many=True).data})

        rows = fetch_all(
            "SELECT * FROM marts.mart_member_utilization ORDER BY total_paid DESC LIMIT 500"
        )
        return Response({"aggregate_only": False, "results": MemberUtilizationSerializer(rows, many=True).data})


ABOUT_PROJECT = {
    "project_name": "Healthcare Claims Analytics Warehouse",
    "portfolio_angle": (
        "Built a HIPAA-aware healthcare claims analytics warehouse using Python, Django, React, "
        "PostgreSQL, advanced SQL, role-based views, masked identifiers, audit logging, export "
        "controls, and data quality checks."
    ),
    "synthetic_data_notice": "Synthetic data only. No real PHI is used in this portfolio project.",
    "hipaa_aware_disclaimer": (
        "This project uses synthetic healthcare claims data only. It is designed to demonstrate "
        "HIPAA-aware engineering patterns such as role-based access, minimum necessary views, "
        "masked identifiers, audit logging, export controls, retention settings, and "
        "de-identification-oriented reporting. It is not presented as a certified HIPAA-compliant "
        "production system. A production deployment handling real ePHI would require legal review, "
        "risk analysis, Business Associate Agreements, secure hosting, operational safeguards, "
        "policies, monitoring, and staff procedures."
    ),
    "architecture": [
        "raw schema: synthetic source-shaped tables (Django-managed)",
        "staging schema: typed/cleaned views over raw",
        "warehouse schema: dimensional model (SCD2 dim_member, type-1 dims, 5 fact tables)",
        "marts schema: 9 analytics-ready aggregate tables",
        "audit schema: audit_events for sensitive-action logging",
        "compliance schema: data_quality_results + compliance dashboard data",
        "Django REST Framework API layer with role-aware, masking-aware views",
        "React + TypeScript + Tailwind dashboard with a demo RoleSwitcher",
    ],
    "data_model_summary": (
        "Raw synthetic claims data flows through staging cleanup views into a dimensional "
        "warehouse (dims + facts joined on surrogate analytics_*_key columns), then into "
        "9 marts that power every dashboard page."
    ),
    "roadmap": [
        "Add authentication (real login) layered on top of the existing role model",
        "Materialized views + scheduled refresh for marts instead of truncate/reload",
        "Expand SCD2 history tracking to providers and payers",
        "Add a de-identification/anonymization scoring mart",
        "Add CSV/Parquet export to object storage with signed URLs",
    ],
}


class AboutProjectView(APIView):
    def get(self, request):
        return Response(ABOUT_PROJECT)
