from unittest.mock import patch

from django.test import TestCase

from apps.compliance.models import AuditEvent
from apps.warehouse.services import exports


class ExportControlTests(TestCase):
    def test_export_requires_a_reason(self):
        with self.assertRaises(exports.ExportNotAllowed):
            exports.create_export(role="Admin", export_type="aggregate_claims", reason="  ")

    def test_export_requires_permitted_role(self):
        with self.assertRaises(exports.ExportNotAllowed):
            exports.create_export(role="Manager", export_type="masked_claims", reason="review")

        self.assertTrue(
            AuditEvent.objects.filter(action="ACCESS_DENIED", resource_id="masked_claims").exists()
        )

    @patch("apps.warehouse.services.exports._fetch")
    def test_permitted_export_returns_csv_and_logs_audit_event(self, mock_fetch):
        mock_fetch.return_value = (["month_date", "total_claims"], [("2026-01-01", 42)])

        result = exports.create_export(role="Manager", export_type="aggregate_claims", reason="monthly board report")

        self.assertEqual(result.row_count, 1)
        self.assertIn("month_date,total_claims", result.content)
        self.assertTrue(
            AuditEvent.objects.filter(action="REPORT_EXPORTED", resource_id="aggregate_claims").exists()
        )

    @patch("apps.warehouse.services.exports._fetch")
    def test_masked_claims_export_masks_claim_id(self, mock_fetch):
        mock_fetch.return_value = (
            ["claim_id", "claim_status"],
            [("CLM-2026-000938", "Paid")],
        )

        result = exports.create_export(role="Claims Analyst", export_type="masked_claims", reason="audit sample")

        self.assertIn("CLM-••••0938", result.content)
        self.assertNotIn("CLM-2026-000938", result.content)
