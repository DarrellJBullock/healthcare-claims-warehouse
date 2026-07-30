"""
Raw-layer models for the Healthcare Claims Analytics Warehouse.

Synthetic data only. No real PHI is used in this portfolio project.

These models are Django's ownership of schema `raw` (the only schema Django
migrates/writes to directly). Everything downstream -- staging, warehouse,
marts -- is built by running the SQL files in backend/sql/ via the
build_marts / run_quality_checks management commands.

db_table uses the `"schema"."table` embedded-quote trick so Django's query
quoting produces a correctly schema-qualified identifier, e.g.
db_table = 'raw"."raw_members' -> quoted as "raw"."raw_members".
"""

from django.db import models


class RawMember(models.Model):
    member_id = models.CharField(max_length=32, primary_key=True)
    subscriber_id = models.CharField(max_length=32)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    plan_type = models.CharField(max_length=50)
    effective_date = models.DateField()
    term_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'raw"."raw_members'
        ordering = ["member_id"]

    def __str__(self):
        return self.member_id


class RawProvider(models.Model):
    provider_id = models.CharField(max_length=32, primary_key=True)
    provider_name = models.CharField(max_length=150)
    specialty = models.CharField(max_length=100)
    npi = models.CharField(max_length=20)
    network_status = models.CharField(max_length=30)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'raw"."raw_providers'
        ordering = ["provider_id"]

    def __str__(self):
        return self.provider_name


class RawPayer(models.Model):
    payer_id = models.CharField(max_length=32, primary_key=True)
    payer_name = models.CharField(max_length=150)
    payer_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'raw"."raw_payers'
        ordering = ["payer_id"]

    def __str__(self):
        return self.payer_name


class RawDiagnosisCategory(models.Model):
    diagnosis_category_code = models.CharField(max_length=20, primary_key=True)
    diagnosis_category_name = models.CharField(max_length=150)

    class Meta:
        db_table = 'raw"."raw_diagnosis_categories'

    def __str__(self):
        return self.diagnosis_category_name


class RawProcedureCategory(models.Model):
    procedure_category_code = models.CharField(max_length=20, primary_key=True)
    procedure_category_name = models.CharField(max_length=150)

    class Meta:
        db_table = 'raw"."raw_procedure_categories'

    def __str__(self):
        return self.procedure_category_name


class RawDenialCode(models.Model):
    denial_code = models.CharField(max_length=20, primary_key=True)
    denial_reason = models.CharField(max_length=200)
    denial_category = models.CharField(max_length=100)

    class Meta:
        db_table = 'raw"."raw_denial_codes'

    def __str__(self):
        return self.denial_reason


class RawClaim(models.Model):
    claim_id = models.CharField(max_length=32, primary_key=True)
    member = models.ForeignKey(RawMember, on_delete=models.CASCADE, db_column="member_id", to_field="member_id")
    provider = models.ForeignKey(RawProvider, on_delete=models.CASCADE, db_column="provider_id", to_field="provider_id")
    payer = models.ForeignKey(RawPayer, on_delete=models.CASCADE, db_column="payer_id", to_field="payer_id")
    claim_type = models.CharField(max_length=50)
    claim_status = models.CharField(max_length=30)
    diagnosis_category = models.ForeignKey(
        RawDiagnosisCategory, on_delete=models.SET_NULL, null=True,
        db_column="diagnosis_category_code", to_field="diagnosis_category_code",
    )
    denial_code = models.ForeignKey(
        RawDenialCode, on_delete=models.SET_NULL, null=True, blank=True,
        db_column="denial_code", to_field="denial_code",
    )
    service_date_start = models.DateField()
    service_date_end = models.DateField()
    submitted_date = models.DateField()
    billed_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'raw"."raw_claims'
        ordering = ["-service_date_start"]

    def __str__(self):
        return self.claim_id


class RawClaimServiceLine(models.Model):
    service_line_id = models.CharField(max_length=40, primary_key=True)
    claim = models.ForeignKey(RawClaim, on_delete=models.CASCADE, db_column="claim_id", to_field="claim_id")
    line_number = models.PositiveIntegerField()
    procedure_category = models.ForeignKey(
        RawProcedureCategory, on_delete=models.SET_NULL, null=True,
        db_column="procedure_category_code", to_field="procedure_category_code",
    )
    service_date = models.DateField()
    units = models.PositiveIntegerField(default=1)
    billed_amount = models.DecimalField(max_digits=12, decimal_places=2)
    allowed_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'raw"."raw_claim_service_lines'
        ordering = ["claim_id", "line_number"]


class RawPayment(models.Model):
    payment_id = models.CharField(max_length=32, primary_key=True)
    claim = models.ForeignKey(RawClaim, on_delete=models.CASCADE, db_column="claim_id", to_field="claim_id")
    payment_date = models.DateField()
    payment_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'raw"."raw_payments'
        ordering = ["-payment_date"]


class RawAdjustment(models.Model):
    adjustment_id = models.CharField(max_length=32, primary_key=True)
    claim = models.ForeignKey(RawClaim, on_delete=models.CASCADE, db_column="claim_id", to_field="claim_id")
    adjustment_type = models.CharField(max_length=50)
    adjustment_amount = models.DecimalField(max_digits=12, decimal_places=2)
    adjustment_date = models.DateField()
    reason_code = models.CharField(max_length=30, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'raw"."raw_adjustments'
        ordering = ["-adjustment_date"]


class RawEligibility(models.Model):
    eligibility_id = models.CharField(max_length=32, primary_key=True)
    member = models.ForeignKey(RawMember, on_delete=models.CASCADE, db_column="member_id", to_field="member_id")
    coverage_start = models.DateField()
    coverage_end = models.DateField(null=True, blank=True)
    plan_type = models.CharField(max_length=50)
    status = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'raw"."raw_eligibility'
        ordering = ["member_id", "coverage_start"]
