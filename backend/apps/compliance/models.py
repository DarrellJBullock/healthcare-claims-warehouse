"""
Audit and compliance models.

Synthetic data only. No real PHI is used in this portfolio project.
Django owns and migrates the `audit` and `compliance` schemas directly
(unlike warehouse/marts, which are built from SQL files).
"""

from django.db import models


class AuditEvent(models.Model):
    ACTION_CHOICES = [
        ("CLAIM_DETAIL_VIEWED", "Claim Detail Viewed"),
        ("MEMBER_DETAIL_VIEWED", "Member Detail Viewed"),
        ("REPORT_EXPORTED", "Report Exported"),
        ("ROLE_CHANGED", "Role Changed"),
        ("ACCESS_DENIED", "Access Denied"),
        ("DATA_QUALITY_CHECK_RUN", "Data Quality Check Run"),
        ("DATA_QUALITY_CHECK_FAILED", "Data Quality Check Failed"),
        ("RETENTION_JOB_RAN", "Retention Job Ran"),
    ]
    STATUS_CHOICES = [
        ("SUCCESS", "Success"),
        ("DENIED", "Denied"),
        ("ERROR", "Error"),
    ]

    event_timestamp = models.DateTimeField(auto_now_add=True)
    user_id = models.CharField(max_length=64)
    user_role = models.CharField(max_length=32)
    action = models.CharField(max_length=64, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=64, blank=True)
    resource_id = models.CharField(max_length=64, blank=True)
    reason = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="SUCCESS")
    # Demo-only placeholder -- never store a real client IP for this
    # synthetic-data portfolio project.
    ip_address_placeholder = models.CharField(max_length=32, default="0.0.0.0")

    class Meta:
        db_table = 'audit"."audit_events'
        ordering = ["-event_timestamp"]

    def __str__(self):
        return f"{self.action} by {self.user_role} @ {self.event_timestamp}"


class DataQualityResult(models.Model):
    SEVERITY_CHOICES = [("HIGH", "High"), ("MEDIUM", "Medium"), ("LOW", "Low")]
    STATUS_CHOICES = [("PASS", "Pass"), ("FAIL", "Fail")]

    check_name = models.CharField(max_length=100)
    table_name = models.CharField(max_length=100)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    failed_count = models.IntegerField(default=0)
    sample_record_key = models.CharField(max_length=64, null=True, blank=True)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'compliance"."data_quality_results'
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.check_name}: {self.status}"
