"""
End-to-end role-based access control tests against the real HTTP API.

These codify the manual QA sweep performed across all 6 demo roles and
every route (Claims, Members, Data Quality, Compliance, Audit Log,
Exports) -- including the exact regressions found and fixed during that
sweep:

  * the claims list endpoint had no role gate at all (fixed by gating on
    can_view_row_level_claims)
  * member utilization was gated on the wrong permission, leaking
    row-level member data to Data Engineer/Auditor (fixed by gating on
    can_view_member_detail)
  * claim detail drilldown 404'd for every masked role because the
    frontend/URL used the maskable claim_id instead of the surrogate
    analytics_claim_key
  * a data-quality 403 path wasn't logging ACCESS_DENIED
  * failed_access_attempts_last_30_days returned a misleading 0 instead
    of null when hidden from a role

Unlike tests/test_roles.py (which unit-tests the permission matrix in
isolation), these hit the actual DRF views over a real warehouse/marts
dataset built via the same build_marts pipeline used in production, so
a regression in the SQL, the view, or the URL wiring is caught here.
"""

import io
import json
from datetime import date

from django.core.management import call_command
from django.db import connection
from django.test import TransactionTestCase

from apps.compliance.models import AuditEvent
from apps.warehouse.models import (
    RawClaim,
    RawClaimServiceLine,
    RawDenialCode,
    RawDiagnosisCategory,
    RawMember,
    RawPayer,
    RawProcedureCategory,
    RawProvider,
)
from apps.warehouse.services import masking

ALL_ROLES = ["Admin", "Data Engineer", "Claims Analyst", "Manager", "Auditor", "Read Only"]

# Expected access, matching the Access Control Matrix shown on the
# Compliance Dashboard -- the source of truth this suite guards.
ROW_LEVEL_CLAIMS_ROLES = {"Admin", "Data Engineer", "Claims Analyst"}
MEMBER_DETAIL_ROLES = {"Admin", "Claims Analyst"}
DATA_QUALITY_ROLES = {"Admin", "Data Engineer"}
COMPLIANCE_ROLES = {"Admin", "Auditor"}
AUDIT_LOG_ROLES = {"Admin", "Auditor"}
EXPORT_TYPE_ROLES = {
    "aggregate_claims": {"Admin", "Manager", "Data Engineer", "Claims Analyst", "Auditor"},
    "masked_claims": {"Admin", "Claims Analyst"},
    "data_quality_report": {"Admin", "Data Engineer"},
    "audit_report": {"Admin", "Auditor"},
}


def role_headers(role):
    return {"HTTP_X_DEMO_ROLE": role}


class WarehouseAPITestCase(TransactionTestCase):
    """Seeds a minimal raw dataset and builds it through the real
    build_marts pipeline, so tests exercise the same SQL path as
    production rather than mocking the warehouse layer.

    Uses TransactionTestCase (not TestCase) because build_marts's
    indexes step runs CREATE INDEX against raw.* tables; Postgres
    refuses to do that within the same transaction as a prior INSERT
    into that table, which is exactly what TestCase's single wrapping
    transaction would do. Production never hits this because seeding
    and build_marts are separate management-command invocations
    (separate transactions) -- TransactionTestCase reproduces that.
    """

    def setUp(self):
        self.member = RawMember.objects.create(
            member_id="MBR-TEST0001", subscriber_id="SUB-TEST0001",
            first_name="Test", last_name="Member", date_of_birth=date(1990, 1, 1),
            gender="Female", address="1 Test St, Testville, TS", phone="555-000-0001",
            email="test.member@example.com", plan_type="PPO", effective_date=date(2024, 1, 1),
        )
        self.provider = RawProvider.objects.create(
            provider_id="PRV-TEST01", provider_name="Test Clinic", specialty="Family Medicine",
            npi="1234567890", network_status="In-Network", address="2 Test St", phone="555-000-0002",
        )
        self.payer = RawPayer.objects.create(
            payer_id="PAY-TEST1", payer_name="Test Health Plan", payer_type="Commercial",
        )
        self.diagnosis = RawDiagnosisCategory.objects.create(
            diagnosis_category_code="Z00-TEST", diagnosis_category_name="General Health Exam",
        )
        self.procedure = RawProcedureCategory.objects.create(
            procedure_category_code="99213-TEST", procedure_category_name="Office Visit",
        )
        self.denial_code = RawDenialCode.objects.create(
            denial_code="CO-16-TEST", denial_reason="Documentation missing", denial_category="Documentation",
        )

        self.paid_claim = RawClaim.objects.create(
            claim_id="CLM-TEST-000001", member=self.member, provider=self.provider, payer=self.payer,
            claim_type="Professional", claim_status="Paid", diagnosis_category=self.diagnosis,
            service_date_start=date(2026, 1, 5), service_date_end=date(2026, 1, 5),
            submitted_date=date(2026, 1, 8), billed_amount=1000, paid_amount=900,
        )
        RawClaimServiceLine.objects.create(
            service_line_id="CLM-TEST-000001-L1", claim=self.paid_claim, line_number=1,
            procedure_category=self.procedure, service_date=date(2026, 1, 5),
            units=1, billed_amount=1000, allowed_amount=950, paid_amount=900,
        )

        self.denied_claim = RawClaim.objects.create(
            claim_id="CLM-TEST-000002", member=self.member, provider=self.provider, payer=self.payer,
            claim_type="Professional", claim_status="Denied", diagnosis_category=self.diagnosis,
            denial_code=self.denial_code,
            service_date_start=date(2026, 1, 10), service_date_end=date(2026, 1, 10),
            submitted_date=date(2026, 1, 12), billed_amount=500, paid_amount=0,
        )
        RawClaimServiceLine.objects.create(
            service_line_id="CLM-TEST-000002-L1", claim=self.denied_claim, line_number=1,
            procedure_category=self.procedure, service_date=date(2026, 1, 10),
            units=1, billed_amount=500, allowed_amount=500, paid_amount=0,
        )

        call_command("build_marts", stdout=io.StringIO())

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT analytics_claim_key FROM warehouse.fact_claim WHERE claim_id = %s",
                [self.paid_claim.claim_id],
            )
            self.paid_claim_key = cursor.fetchone()[0]

    def tearDown(self):
        # TransactionTestCase's automatic between-test flush doesn't
        # reliably reach these schema-qualified tables (the `"schema"."table`
        # db_table trick confuses its table-name introspection), so clean up
        # explicitly -- including audit.audit_events, which reset_warehouse
        # deliberately preserves in production but tests need cleared for
        # isolation between test methods.
        with connection.cursor() as cursor:
            cursor.execute(
                """
                TRUNCATE TABLE
                    warehouse.fact_eligibility_coverage, warehouse.fact_adjustment, warehouse.fact_payment,
                    warehouse.fact_claim_service_line, warehouse.fact_claim,
                    warehouse.dim_member, warehouse.dim_provider, warehouse.dim_payer,
                    warehouse.dim_diagnosis_category, warehouse.dim_procedure_category, warehouse.dim_denial_reason,
                    marts.mart_claims_summary, marts.mart_denial_trends, marts.mart_provider_performance,
                    marts.mart_payer_performance, marts.mart_member_utilization, marts.mart_payment_reconciliation,
                    marts.mart_monthly_claims_kpis, marts.mart_data_quality_scorecard, marts.mart_compliance_audit_summary,
                    compliance.data_quality_results,
                    raw.raw_adjustments, raw.raw_payments, raw.raw_claim_service_lines, raw.raw_claims,
                    raw.raw_eligibility, raw.raw_members, raw.raw_providers, raw.raw_payers,
                    raw.raw_denial_codes, raw.raw_diagnosis_categories, raw.raw_procedure_categories,
                    audit.audit_events
                CASCADE
                """
            )


class ClaimsListPermissionTests(WarehouseAPITestCase):
    def test_role_matrix(self):
        for role in ALL_ROLES:
            with self.subTest(role=role):
                response = self.client.get("/api/claims/", **role_headers(role))
                expected = 200 if role in ROW_LEVEL_CLAIMS_ROLES else 403
                self.assertEqual(response.status_code, expected)

    def test_denied_role_logs_access_denied(self):
        self.client.get("/api/claims/", **role_headers("Manager"))
        self.assertTrue(
            AuditEvent.objects.filter(action="ACCESS_DENIED", resource_type="claim_list", user_role="Manager").exists()
        )

    def test_masked_role_never_sees_raw_claim_id(self):
        response = self.client.get("/api/claims/", **role_headers("Claims Analyst"))
        claim_ids = [row["claim_id"] for row in response.json()["results"]]
        self.assertTrue(all("•" in cid for cid in claim_ids))
        self.assertNotIn(self.paid_claim.claim_id, claim_ids)

    def test_admin_sees_unmasked_claim_id(self):
        response = self.client.get("/api/claims/", **role_headers("Admin"))
        claim_ids = [row["claim_id"] for row in response.json()["results"]]
        self.assertIn(self.paid_claim.claim_id, claim_ids)

    def test_every_row_includes_analytics_claim_key_for_routing(self):
        response = self.client.get("/api/claims/", **role_headers("Admin"))
        for row in response.json()["results"]:
            self.assertIsInstance(row["analytics_claim_key"], int)


class ClaimDetailPermissionTests(WarehouseAPITestCase):
    def test_role_matrix(self):
        for role in ALL_ROLES:
            with self.subTest(role=role):
                response = self.client.get(f"/api/claims/{self.paid_claim_key}/", **role_headers(role))
                expected = 200 if role in ROW_LEVEL_CLAIMS_ROLES else 403
                self.assertEqual(response.status_code, expected)

    def test_unknown_analytics_claim_key_returns_404_not_500(self):
        response = self.client.get("/api/claims/999999999/", **role_headers("Admin"))
        self.assertEqual(response.status_code, 404)

    def test_masked_role_gets_masked_identifiers_and_service_lines(self):
        response = self.client.get(f"/api/claims/{self.paid_claim_key}/", **role_headers("Claims Analyst"))
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["claim_id"], masking.mask_identifier(self.paid_claim.claim_id))
        self.assertEqual(body["member_id"], masking.mask_identifier(self.member.member_id))
        self.assertEqual(len(body["service_lines"]), 1)

    def test_admin_gets_unmasked_identifiers(self):
        response = self.client.get(f"/api/claims/{self.paid_claim_key}/", **role_headers("Admin"))
        body = response.json()
        self.assertEqual(body["claim_id"], self.paid_claim.claim_id)
        self.assertEqual(body["member_id"], self.member.member_id)

    def test_audit_trail_always_logs_the_real_unmasked_claim_id(self):
        self.client.get(f"/api/claims/{self.paid_claim_key}/", **role_headers("Claims Analyst"))
        event = AuditEvent.objects.filter(action="CLAIM_DETAIL_VIEWED", user_role="Claims Analyst").latest("event_timestamp")
        self.assertEqual(event.resource_id, self.paid_claim.claim_id)

    def test_denied_role_logs_access_denied_with_key_as_resource_id(self):
        self.client.get(f"/api/claims/{self.paid_claim_key}/", **role_headers("Read Only"))
        self.assertTrue(
            AuditEvent.objects.filter(
                action="ACCESS_DENIED", resource_type="claim", resource_id=str(self.paid_claim_key),
            ).exists()
        )


class MemberUtilizationPermissionTests(WarehouseAPITestCase):
    def test_row_level_detail_only_for_admin_and_claims_analyst(self):
        for role in ALL_ROLES:
            with self.subTest(role=role):
                response = self.client.get("/api/members/utilization/", **role_headers(role))
                self.assertEqual(response.status_code, 200)
                body = response.json()
                expected_aggregate_only = role not in MEMBER_DETAIL_ROLES
                self.assertEqual(body["aggregate_only"], expected_aggregate_only)

    def test_aggregate_view_never_includes_a_member_key(self):
        response = self.client.get("/api/members/utilization/", **role_headers("Data Engineer"))
        body = response.json()
        self.assertTrue(body["aggregate_only"])
        for row in body["results"]:
            self.assertNotIn("analytics_member_key", row)

    def test_detail_view_uses_surrogate_key_not_raw_member_id(self):
        response = self.client.get("/api/members/utilization/", **role_headers("Claims Analyst"))
        body = response.json()
        self.assertFalse(body["aggregate_only"])
        for row in body["results"]:
            self.assertIn("analytics_member_key", row)
            self.assertNotIn("member_id", row)


class DataQualityPermissionTests(WarehouseAPITestCase):
    def test_results_role_matrix(self):
        for role in ALL_ROLES:
            with self.subTest(role=role):
                response = self.client.get("/api/data-quality/results/", **role_headers(role))
                expected = 200 if role in DATA_QUALITY_ROLES else 403
                self.assertEqual(response.status_code, expected)

    def test_run_role_matrix(self):
        for role in ALL_ROLES:
            with self.subTest(role=role):
                response = self.client.post("/api/data-quality/run/", **role_headers(role))
                expected = 200 if role in DATA_QUALITY_ROLES else 403
                self.assertEqual(response.status_code, expected)

    def test_denied_results_request_logs_access_denied(self):
        self.client.get("/api/data-quality/results/", **role_headers("Auditor"))
        self.assertTrue(
            AuditEvent.objects.filter(action="ACCESS_DENIED", resource_type="data_quality_results", user_role="Auditor").exists()
        )

    def test_denied_run_request_logs_access_denied(self):
        self.client.post("/api/data-quality/run/", **role_headers("Auditor"))
        self.assertTrue(
            AuditEvent.objects.filter(action="ACCESS_DENIED", resource_type="data_quality_run", user_role="Auditor").exists()
        )


class AuditLogPermissionTests(WarehouseAPITestCase):
    def test_role_matrix(self):
        for role in ALL_ROLES:
            with self.subTest(role=role):
                response = self.client.get("/api/audit-log/", **role_headers(role))
                expected = 200 if role in AUDIT_LOG_ROLES else 403
                self.assertEqual(response.status_code, expected)

    def test_denied_role_logs_access_denied(self):
        self.client.get("/api/audit-log/", **role_headers("Manager"))
        self.assertTrue(
            AuditEvent.objects.filter(action="ACCESS_DENIED", resource_type="audit_log", user_role="Manager").exists()
        )

    def test_response_is_paginated_not_capped_silently(self):
        for i in range(30):
            AuditEvent.objects.create(user_role="Admin", action="ROLE_CHANGED", resource_type="role_switcher", reason=str(i))
        response = self.client.get("/api/audit-log/", **role_headers("Admin"))
        body = response.json()
        self.assertIn("count", body)
        self.assertIn("next", body)
        self.assertGreater(body["count"], len(body["results"]))


class ComplianceSummaryPermissionTests(WarehouseAPITestCase):
    def setUp(self):
        AuditEvent.objects.create(user_role="Read Only", action="ACCESS_DENIED", resource_type="claim_list")
        AuditEvent.objects.create(
            user_role="Admin", action="REPORT_EXPORTED", resource_type="export", resource_id="aggregate_claims",
        )
        AuditEvent.objects.create(user_role="Admin", action="CLAIM_DETAIL_VIEWED", resource_type="claim", resource_id="CLM-TEST-000001")

    def test_sensitive_fields_are_null_not_zero_when_hidden(self):
        for role in ALL_ROLES:
            with self.subTest(role=role):
                response = self.client.get("/api/compliance/summary/", **role_headers(role))
                body = response.json()
                if role in COMPLIANCE_ROLES:
                    self.assertIsNotNone(body["failed_access_attempts_last_30_days"])
                    self.assertIsNotNone(body["last_export"])
                    self.assertIsNotNone(body["last_sensitive_view_event"])
                    self.assertTrue(len(body["checklist"]) > 0)
                else:
                    self.assertIsNone(body["failed_access_attempts_last_30_days"])
                    self.assertIsNone(body["last_export"])
                    self.assertIsNone(body["last_sensitive_view_event"])
                    self.assertEqual(body["checklist"], [])

    def test_public_fields_always_visible(self):
        response = self.client.get("/api/compliance/summary/", **role_headers("Read Only"))
        body = response.json()
        self.assertTrue(body["synthetic_data_only"])
        self.assertIn("retention_policy", body)


class ExportsPermissionTests(WarehouseAPITestCase):
    def _post(self, role, export_type, reason="test reason"):
        return self.client.post(
            "/api/exports/", data=json.dumps({"export_type": export_type, "reason": reason}),
            content_type="application/json", **role_headers(role),
        )

    def test_full_role_by_export_type_matrix(self):
        for export_type, allowed_roles in EXPORT_TYPE_ROLES.items():
            for role in ALL_ROLES:
                with self.subTest(export_type=export_type, role=role):
                    response = self._post(role, export_type)
                    expected = 200 if role in allowed_roles else 403
                    self.assertEqual(response.status_code, expected)

    def test_reason_is_required(self):
        # DRF's CharField trims whitespace and rejects blank strings at
        # the serializer level (400) before the service layer's own
        # reason.strip() check would ever fire (403).
        response = self._post("Admin", "aggregate_claims", reason="   ")
        self.assertEqual(response.status_code, 400)

    def test_masked_claims_export_content_is_masked(self):
        response = self._post("Claims Analyst", "masked_claims", reason="coding review sample")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn(masking.mask_identifier(self.paid_claim.claim_id), content)
        self.assertNotIn(self.paid_claim.claim_id, content)

    def test_successful_export_logs_report_exported(self):
        self._post("Admin", "aggregate_claims", reason="board report")
        self.assertTrue(
            AuditEvent.objects.filter(action="REPORT_EXPORTED", user_role="Admin", resource_id="aggregate_claims").exists()
        )

    def test_denied_export_logs_access_denied(self):
        self._post("Read Only", "audit_report", reason="trying anyway")
        self.assertTrue(
            AuditEvent.objects.filter(action="ACCESS_DENIED", user_role="Read Only", resource_id="audit_report").exists()
        )
