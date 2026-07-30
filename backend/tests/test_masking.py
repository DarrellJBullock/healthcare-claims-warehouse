from datetime import date

from django.test import SimpleTestCase

from apps.warehouse.services import masking


class MaskIdentifierTests(SimpleTestCase):
    def test_member_id_example_from_spec(self):
        self.assertEqual(masking.mask_identifier("MBR-10039281"), "MBR-••••9281")

    def test_claim_id_example_from_spec(self):
        self.assertEqual(masking.mask_identifier("CLM-2026-000938"), "CLM-••••0938")

    def test_empty_value_passthrough(self):
        self.assertEqual(masking.mask_identifier(""), "")
        self.assertIsNone(masking.mask_identifier(None))


class MaskFieldTests(SimpleTestCase):
    def test_mask_date_of_birth_keeps_only_year(self):
        self.assertEqual(masking.mask_date_of_birth(date(1985, 6, 12)), "1985-**-**")

    def test_mask_phone_keeps_last_four(self):
        self.assertEqual(masking.mask_phone("555-123-4567"), "•••-•••-4567")

    def test_mask_email_keeps_first_char_and_domain(self):
        self.assertEqual(masking.mask_email("jane.doe@example.com"), "j•••@example.com")

    def test_mask_address_keeps_last_segment(self):
        self.assertEqual(masking.mask_address("123 Main St, Springfield, IL"), "••••••, IL")


class MaskPayloadTests(SimpleTestCase):
    def test_mask_claim_payload_masks_ids_when_enabled(self):
        payload = {"claim_id": "CLM-2026-000938", "member_id": "MBR-10039281", "claim_status": "Paid"}
        masked = masking.mask_claim_payload(payload, mask=True)
        self.assertEqual(masked["claim_id"], "CLM-••••0938")
        self.assertEqual(masked["member_id"], "MBR-••••9281")
        self.assertEqual(masked["claim_status"], "Paid")

    def test_mask_claim_payload_passthrough_when_disabled(self):
        payload = {"claim_id": "CLM-2026-000938"}
        self.assertEqual(masking.mask_claim_payload(payload, mask=False), payload)
