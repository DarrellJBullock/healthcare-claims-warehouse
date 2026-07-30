-- Mart: data quality scorecard, aggregated from the latest run of each
-- named check in compliance.data_quality_results (populated by the
-- run_quality_checks management command).

CREATE TABLE IF NOT EXISTS marts.mart_data_quality_scorecard (
    table_name      text PRIMARY KEY,
    total_checks    integer NOT NULL,
    passed_checks   integer NOT NULL,
    failed_checks   integer NOT NULL,
    quality_score   numeric(5, 2) NOT NULL,
    last_run_at     timestamptz
);

TRUNCATE marts.mart_data_quality_scorecard;

WITH latest_per_check AS (
    SELECT DISTINCT ON (table_name, check_name)
        table_name, check_name, status, created_at
    FROM compliance.data_quality_results
    ORDER BY table_name, check_name, created_at DESC
)
INSERT INTO marts.mart_data_quality_scorecard (
    table_name, total_checks, passed_checks, failed_checks, quality_score, last_run_at
)
SELECT
    table_name,
    count(*) AS total_checks,
    sum(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) AS passed_checks,
    sum(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) AS failed_checks,
    ROUND(
        100.0 * sum(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) / NULLIF(count(*), 0),
        2
    ) AS quality_score,
    max(created_at) AS last_run_at
FROM latest_per_check
GROUP BY table_name
ORDER BY quality_score ASC;
