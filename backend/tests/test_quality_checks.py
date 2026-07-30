from datetime import date

from django.test import TestCase

from apps.compliance.models import DataQualityResult
from apps.warehouse.models import RawClaim, RawMember, RawPayer, RawProvider
from apps.warehouse.services import data_quality


class DataQualityChecksTests(TestCase):
    def setUp(self):
        self.member = RawMember.objects.create(
            member_id="MBR-10000001", subscriber_id="SUB-10000001",
            first_name="Test", last_name="Member", date_of_birth=date(1990, 1, 1),
            gender="Female", address="1 Test St, Testville, TS", phone="555-000-0001",
            email="test.member@example.com", plan_type="PPO", effective_date=date(2024, 1, 1),
        )
        self.provider = RawProvider.objects.create(
            provider_id="PRV-90001", provider_name="Test Clinic", specialty="Family Medicine",
            npi="1234567890", network_status="In-Network", address="2 Test St", phone="555-000-0002",
        )
        self.payer = RawPayer.objects.create(
            payer_id="PAY-900", payer_name="Test Health Plan", payer_type="Commercial",
        )

    def test_paid_amount_exceeds_billed_check_fails_when_violated(self):
        RawClaim.objects.create(
            claim_id="CLM-2026-900001", member=self.member, provider=self.provider, payer=self.payer,
            claim_type="Professional", claim_status="Paid",
            service_date_start=date(2026, 1, 1), service_date_end=date(2026, 1, 1),
            submitted_date=date(2026, 1, 5), billed_amount=100, paid_amount=500,
        )

        summary = data_quality.run_all_checks(triggered_by_role="Data Engineer")

        self.assertEqual(summary["total_checks"], 15)
        result = DataQualityResult.objects.get(check_name="paid_amount_exceeds_billed")
        self.assertEqual(result.status, "FAIL")
        self.assertGreaterEqual(result.failed_count, 1)

    def test_clean_data_passes_required_field_checks(self):
        RawClaim.objects.create(
            claim_id="CLM-2026-900002", member=self.member, provider=self.provider, payer=self.payer,
            claim_type="Professional", claim_status="Paid",
            service_date_start=date(2026, 1, 1), service_date_end=date(2026, 1, 1),
            submitted_date=date(2026, 1, 5), billed_amount=100, paid_amount=80,
        )

        data_quality.run_all_checks(triggered_by_role="Data Engineer")

        result = DataQualityResult.objects.get(check_name="required_claim_fields")
        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.failed_count, 0)
