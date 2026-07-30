from django.test import SimpleTestCase

from apps.warehouse.services import roles


class RolePermissionTests(SimpleTestCase):
    def test_admin_sees_everything(self):
        perms = roles.get_permissions("Admin")
        self.assertTrue(perms["can_view_compliance"])
        self.assertTrue(perms["can_manage_role_controls"])
        self.assertFalse(perms["mask_identifiers"])

    def test_manager_is_aggregate_only(self):
        perms = roles.get_permissions("Manager")
        self.assertTrue(perms["can_view_aggregate_only"])
        self.assertFalse(perms["can_view_member_detail"])
        self.assertFalse(perms["can_view_row_level_claims"])

    def test_claims_analyst_sees_masked_row_level_claims(self):
        perms = roles.get_permissions("Claims Analyst")
        self.assertTrue(perms["can_view_row_level_claims"])
        self.assertTrue(perms["mask_identifiers"])

    def test_auditor_sees_audit_and_compliance_only(self):
        perms = roles.get_permissions("Auditor")
        self.assertTrue(perms["can_view_audit_log"])
        self.assertTrue(perms["can_view_compliance"])
        self.assertFalse(perms["can_view_row_level_claims"])

    def test_unknown_role_falls_back_to_read_only(self):
        self.assertEqual(roles.normalize_role("Not A Real Role"), roles.DEFAULT_ROLE)

    def test_can_export_respects_export_type_matrix(self):
        self.assertTrue(roles.can_export("Claims Analyst", "masked_claims"))
        self.assertFalse(roles.can_export("Manager", "masked_claims"))
        self.assertTrue(roles.can_export("Manager", "aggregate_claims"))
        self.assertTrue(roles.can_export("Auditor", "audit_report"))
        self.assertFalse(roles.can_export("Claims Analyst", "audit_report"))
