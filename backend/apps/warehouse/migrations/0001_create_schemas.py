from django.db import migrations

CREATE_SCHEMAS_SQL = """
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS warehouse;
CREATE SCHEMA IF NOT EXISTS marts;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS compliance;
"""


class Migration(migrations.Migration):
    """
    Creates the six warehouse schemas before any schema-qualified tables
    (raw.*, audit.*, compliance.*) are created by later migrations.
    Mirrors backend/sql/schemas/001_create_schemas.sql.
    """

    initial = True
    dependencies = []

    operations = [
        migrations.RunSQL(sql=CREATE_SCHEMAS_SQL, reverse_sql=migrations.RunSQL.noop),
    ]
