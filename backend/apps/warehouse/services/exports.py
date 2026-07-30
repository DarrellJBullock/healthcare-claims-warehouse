"""
Export control service.

Every export requires: a valid role check, a stated business reason, an
audit event, and defaults to masked/aggregate output unless the role is
explicitly entitled to row-level masked exports.
"""

import csv
import io
from dataclasses import dataclass

from django.db import connection

from apps.warehouse.services import audit as audit_service
from apps.warehouse.services import masking, roles


class ExportNotAllowed(Exception):
    pass


@dataclass
class ExportResult:
    export_type: str
    filename: str
    content: str
    row_count: int


def _rows_to_csv(columns, rows) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(columns)
    writer.writerows(rows)
    return buffer.getvalue()


def _fetch(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)
        columns = [c[0] for c in cursor.description]
        rows = cursor.fetchall()
    return columns, rows


def create_export(*, role: str, export_type: str, reason: str, user_id: str = "demo-user") -> ExportResult:
    if not reason or not reason.strip():
        raise ExportNotAllowed("An export reason is required.")

    if not roles.can_export(role, export_type):
        audit_service.log_access_denied(
            user_role=role,
            resource_type="export",
            resource_id=export_type,
            reason=reason,
        )
        raise ExportNotAllowed(f"Role '{role}' is not permitted to run export '{export_type}'.")

    if export_type == "aggregate_claims":
        columns, rows = _fetch(
            "SELECT month_date, total_claims, total_billed, total_paid, denial_rate, avg_paid_amount "
            "FROM marts.mart_claims_summary ORDER BY month_date"
        )
        filename = "aggregate_claims_export.csv"

    elif export_type == "masked_claims":
        columns, rows = _fetch(
            "SELECT claim_id, claim_status, claim_type, billed_amount, paid_amount, service_date_start "
            "FROM warehouse.fact_claim ORDER BY service_date_start DESC LIMIT 500"
        )
        masked_rows = []
        for row in rows:
            row = list(row)
            row[0] = masking.mask_identifier(row[0])
            masked_rows.append(row)
        rows = masked_rows
        filename = "masked_claims_export.csv"

    elif export_type == "data_quality_report":
        columns, rows = _fetch(
            "SELECT check_name, table_name, severity, status, failed_count, message, created_at "
            "FROM compliance.data_quality_results ORDER BY created_at DESC"
        )
        filename = "data_quality_report.csv"

    elif export_type == "audit_report":
        columns, rows = _fetch(
            "SELECT event_timestamp, user_role, action, resource_type, resource_id, status "
            "FROM audit.audit_events ORDER BY event_timestamp DESC LIMIT 1000"
        )
        filename = "audit_report.csv"

    else:
        raise ExportNotAllowed(f"Unknown export type '{export_type}'.")

    content = _rows_to_csv(columns, rows)

    audit_service.log_event(
        user_id=user_id,
        user_role=role,
        action="REPORT_EXPORTED",
        resource_type="export",
        resource_id=export_type,
        reason=reason,
    )

    return ExportResult(export_type=export_type, filename=filename, content=content, row_count=len(rows))
