"""
Executes the SQL-defined data quality checks in backend/sql/quality/ and
records one compliance.data_quality_results row per check.
"""

import re
from pathlib import Path

from django.db import connection

from apps.compliance.models import DataQualityResult
from apps.warehouse.services import audit as audit_service

QUALITY_SQL_DIR = Path(__file__).resolve().parent.parent.parent.parent / "sql" / "quality"

HEADER_RE = re.compile(
    r"--\s*CHECK:\s*(?P<name>[\w\-]+)\s*\|\s*TABLE:\s*(?P<table>[\w\-]+)\s*\|\s*"
    r"SEVERITY:\s*(?P<severity>HIGH|MEDIUM|LOW)\s*\|\s*MESSAGE:\s*(?P<message>.+)"
)


def _parse_checks():
    checks = []
    for sql_file in sorted(QUALITY_SQL_DIR.glob("*.sql")):
        text = sql_file.read_text()
        blocks = re.split(r"(?=-- CHECK:)", text)
        for block in blocks:
            header_match = HEADER_RE.search(block)
            if not header_match:
                continue
            # SQL body is everything after the header line, up to the
            # trailing semicolon.
            body = block[header_match.end():].strip()
            if body.endswith(";"):
                body = body[:-1]
            checks.append(
                {
                    "check_name": header_match.group("name"),
                    "table_name": header_match.group("table"),
                    "severity": header_match.group("severity"),
                    "message": header_match.group("message").strip(),
                    "sql": body,
                }
            )
    return checks


def run_all_checks(*, triggered_by_role: str = "Data Engineer") -> dict:
    checks = _parse_checks()
    results = []
    failed_checks = 0

    with connection.cursor() as cursor:
        for check in checks:
            cursor.execute(check["sql"])
            row = cursor.fetchone()
            failed_count = int(row[0] or 0) if row else 0
            sample_record_key = row[1] if row and len(row) > 1 else None
            status = "FAIL" if failed_count > 0 else "PASS"
            if status == "FAIL":
                failed_checks += 1

            result = DataQualityResult.objects.create(
                check_name=check["check_name"],
                table_name=check["table_name"],
                severity=check["severity"],
                status=status,
                failed_count=failed_count,
                sample_record_key=sample_record_key,
                message=check["message"],
            )
            results.append(result)

            if status == "FAIL":
                audit_service.log_event(
                    user_role=triggered_by_role,
                    action="DATA_QUALITY_CHECK_FAILED",
                    resource_type="data_quality_check",
                    resource_id=check["check_name"],
                    reason=f"{failed_count} failing rows in {check['table_name']}",
                    status="ERROR",
                )

    audit_service.log_event(
        user_role=triggered_by_role,
        action="DATA_QUALITY_CHECK_RUN",
        resource_type="data_quality_suite",
        resource_id="run_quality_checks",
        reason=f"{len(checks)} checks executed, {failed_checks} failed",
    )

    return {
        "total_checks": len(checks),
        "failed_checks": failed_checks,
        "passed_checks": len(checks) - failed_checks,
        "results": results,
    }
