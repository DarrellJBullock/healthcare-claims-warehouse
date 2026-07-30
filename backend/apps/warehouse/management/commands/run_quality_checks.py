from django.core.management.base import BaseCommand

from apps.warehouse.services import data_quality


class Command(BaseCommand):
    help = "Runs the SQL-defined data quality checks and records results in compliance.data_quality_results"

    def handle(self, *args, **options):
        summary = data_quality.run_all_checks(triggered_by_role="Data Engineer")
        self.stdout.write(
            self.style.SUCCESS(
                f"Ran {summary['total_checks']} checks: "
                f"{summary['passed_checks']} passed, {summary['failed_checks']} failed."
            )
        )
        for result in summary["results"]:
            if result.status == "FAIL":
                self.stdout.write(self.style.WARNING(
                    f"  FAIL [{result.severity}] {result.check_name} -> {result.failed_count} rows"
                ))
