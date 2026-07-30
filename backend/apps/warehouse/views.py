from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.compliance.models import DataQualityResult
from apps.warehouse.serializers import (
    ClaimDetailSerializer,
    ClaimListItemSerializer,
    DashboardSummarySerializer,
    DataQualityResultSerializer,
    DataQualityScorecardSerializer,
    ExportRequestSerializer,
)
from apps.warehouse.services import audit as audit_service
from apps.warehouse.services import data_quality as data_quality_service
from apps.warehouse.services import exports as exports_service
from apps.warehouse.services import masking, roles
from apps.warehouse.services.db_utils import fetch_all, fetch_one

SYNTHETIC_DATA_NOTICE = "Synthetic data only. No real PHI is used in this portfolio project."


class DashboardSummaryView(APIView):
    def get(self, request):
        totals = fetch_one(
            """
            SELECT
                COALESCE(sum(total_claims), 0) AS total_claims,
                COALESCE(sum(total_billed), 0) AS total_billed,
                COALESCE(sum(total_paid), 0) AS total_paid,
                COALESCE(sum(denied_claims)::float / NULLIF(sum(total_claims), 0), 0) AS denial_rate,
                COALESCE(sum(total_paid) / NULLIF(sum(total_claims), 0), 0) AS avg_paid_amount
            FROM marts.mart_claims_summary
            """
        ) or {}

        top_denial = fetch_one(
            """
            SELECT denial_reason, sum(denial_count) AS cnt
            FROM marts.mart_denial_trends
            GROUP BY denial_reason
            ORDER BY cnt DESC
            LIMIT 1
            """
        )

        quality_row = fetch_one(
            "SELECT COALESCE(sum(failed_checks), 0) AS open_issues FROM marts.mart_data_quality_scorecard"
        ) or {"open_issues": 0}

        recent_events = fetch_all(
            """
            SELECT event_timestamp, user_role, action, resource_type, status
            FROM audit.audit_events
            ORDER BY event_timestamp DESC
            LIMIT 5
            """
        )

        monthly_trend = fetch_all(
            "SELECT month_date, total_claims, total_billed, total_paid "
            "FROM marts.mart_claims_summary ORDER BY month_date"
        )

        role = roles.role_from_request(request)
        permissions = roles.get_permissions(role)

        data = {
            "total_claims": totals.get("total_claims", 0),
            "total_billed": totals.get("total_billed", 0),
            "total_paid": totals.get("total_paid", 0),
            "avg_paid_amount": totals.get("avg_paid_amount", 0),
            "denial_rate": totals.get("denial_rate", 0),
            "top_denial_reason": top_denial["denial_reason"] if top_denial else None,
            "open_data_quality_issues": quality_row["open_issues"],
            "recent_audit_events": recent_events if permissions["can_view_audit_log"] else [],
            "compliance_status": {
                "masking_enabled": True,
                "audit_logging_enabled": True,
                "export_controls_enabled": True,
                "role_based_access_enabled": True,
            },
            "monthly_trend": monthly_trend,
            "synthetic_data_notice": SYNTHETIC_DATA_NOTICE,
        }
        serializer = DashboardSummarySerializer(data)
        return Response(serializer.data)


CLAIM_FILTER_COLUMNS = {
    "payer": "dpay.payer_name = %s",
    "provider": "dp.provider_name = %s",
    "status": "fc.claim_status = %s",
    "denial_reason": "dr.denial_reason = %s",
    "date_from": "fc.service_date_start >= %s",
    "date_to": "fc.service_date_start <= %s",
}


class ClaimListView(APIView):
    def get(self, request):
        role = roles.role_from_request(request)
        permissions = roles.get_permissions(role)

        where_clauses = []
        params = []
        for query_param, sql_clause in CLAIM_FILTER_COLUMNS.items():
            value = request.query_params.get(query_param)
            if value:
                where_clauses.append(sql_clause)
                params.append(value)
        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        page = max(int(request.query_params.get("page", 1)), 1)
        page_size = min(max(int(request.query_params.get("page_size", 25)), 1), 100)
        offset = (page - 1) * page_size

        count_row = fetch_one(
            f"""
            SELECT count(*) AS total
            FROM warehouse.fact_claim fc
            JOIN warehouse.dim_provider dp ON dp.analytics_provider_key = fc.analytics_provider_key
            JOIN warehouse.dim_payer dpay ON dpay.analytics_payer_key = fc.analytics_payer_key
            LEFT JOIN warehouse.dim_denial_reason dr ON dr.denial_code = fc.denial_code
            {where_sql}
            """,
            params,
        )

        rows = fetch_all(
            f"""
            SELECT
                fc.claim_id, fc.claim_status, fc.claim_type,
                fc.service_date_start, fc.service_date_end,
                fc.billed_amount, fc.paid_amount,
                dp.provider_name, dpay.payer_name, dr.denial_reason
            FROM warehouse.fact_claim fc
            JOIN warehouse.dim_provider dp ON dp.analytics_provider_key = fc.analytics_provider_key
            JOIN warehouse.dim_payer dpay ON dpay.analytics_payer_key = fc.analytics_payer_key
            LEFT JOIN warehouse.dim_denial_reason dr ON dr.denial_code = fc.denial_code
            {where_sql}
            ORDER BY fc.service_date_start DESC
            LIMIT %s OFFSET %s
            """,
            [*params, page_size, offset],
        )

        mask = permissions["mask_identifiers"]
        for row in rows:
            row["claim_id"] = masking.mask_identifier(row["claim_id"]) if mask else row["claim_id"]

        serializer = ClaimListItemSerializer(rows, many=True)
        return Response(
            {
                "count": count_row["total"] if count_row else 0,
                "page": page,
                "page_size": page_size,
                "results": serializer.data,
            }
        )


class ClaimDetailView(APIView):
    def get(self, request, claim_id):
        role = roles.role_from_request(request)
        permissions = roles.get_permissions(role)

        if not permissions["can_view_row_level_claims"]:
            audit_service.log_access_denied(
                user_role=role, resource_type="claim", resource_id=claim_id,
                reason="Role not permitted to view row-level claim detail",
            )
            return Response({"detail": "Not permitted for this role."}, status=403)

        claim = fetch_one(
            """
            SELECT
                fc.claim_id, fc.claim_status, fc.claim_type,
                fc.service_date_start, fc.service_date_end, fc.submitted_date,
                fc.billed_amount, fc.paid_amount,
                dp.provider_name, dpay.payer_name, dr.denial_reason,
                dm.member_id, ddx.diagnosis_category_name
            FROM warehouse.fact_claim fc
            JOIN warehouse.dim_provider dp ON dp.analytics_provider_key = fc.analytics_provider_key
            JOIN warehouse.dim_payer dpay ON dpay.analytics_payer_key = fc.analytics_payer_key
            JOIN warehouse.dim_member dm ON dm.analytics_member_key = fc.analytics_member_key
            LEFT JOIN warehouse.dim_denial_reason dr ON dr.denial_code = fc.denial_code
            LEFT JOIN warehouse.dim_diagnosis_category ddx ON ddx.diagnosis_category_code = fc.diagnosis_category_code
            WHERE fc.claim_id = %s
            """,
            [claim_id],
        )
        if not claim:
            return Response({"detail": "Claim not found."}, status=404)

        claim["service_lines"] = fetch_all(
            """
            SELECT sl.line_number, pc.procedure_category_name, sl.units,
                   sl.billed_amount, sl.allowed_amount, sl.paid_amount
            FROM warehouse.fact_claim_service_line sl
            JOIN warehouse.fact_claim fc ON fc.analytics_claim_key = sl.analytics_claim_key
            LEFT JOIN warehouse.dim_procedure_category pc ON pc.procedure_category_code = sl.procedure_category_code
            WHERE fc.claim_id = %s
            ORDER BY sl.line_number
            """,
            [claim_id],
        )

        mask = permissions["mask_identifiers"]
        if mask:
            claim["claim_id"] = masking.mask_identifier(claim["claim_id"])
            claim["member_id"] = masking.mask_identifier(claim["member_id"])

        audit_service.log_event(
            user_role=role, action="CLAIM_DETAIL_VIEWED",
            resource_type="claim", resource_id=claim_id,
        )

        serializer = ClaimDetailSerializer(claim)
        return Response(serializer.data)


class DataQualityResultsView(APIView):
    def get(self, request):
        role = roles.role_from_request(request)
        permissions = roles.get_permissions(role)
        if not permissions["can_view_data_quality"]:
            return Response({"detail": "Not permitted for this role."}, status=403)

        latest_results = DataQualityResult.objects.all()[:100]
        scorecard = fetch_all("SELECT * FROM marts.mart_data_quality_scorecard ORDER BY quality_score ASC")

        return Response(
            {
                "scorecard": DataQualityScorecardSerializer(scorecard, many=True).data,
                "results": DataQualityResultSerializer(latest_results, many=True).data,
            }
        )


class DataQualityRunView(APIView):
    def post(self, request):
        role = roles.role_from_request(request)
        permissions = roles.get_permissions(role)
        if not permissions["can_run_quality_checks"]:
            audit_service.log_access_denied(
                user_role=role, resource_type="data_quality_run",
                reason="Role not permitted to run data quality checks",
            )
            return Response({"detail": "Not permitted for this role."}, status=403)

        summary = data_quality_service.run_all_checks(triggered_by_role=role)
        return Response(
            {
                "total_checks": summary["total_checks"],
                "passed_checks": summary["passed_checks"],
                "failed_checks": summary["failed_checks"],
            }
        )


class ExportsView(APIView):
    def post(self, request):
        role = roles.role_from_request(request)
        serializer = ExportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = exports_service.create_export(
                role=role,
                export_type=serializer.validated_data["export_type"],
                reason=serializer.validated_data["reason"],
            )
        except exports_service.ExportNotAllowed as exc:
            return Response({"detail": str(exc)}, status=403)

        response = HttpResponse(result.content, content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{result.filename}"'
        response["X-Row-Count"] = str(result.row_count)
        return response
