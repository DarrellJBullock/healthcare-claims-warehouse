-- Mart: member utilization, keyed only by the surrogate analytics_member_key
-- (never raw member_id) with a synthetic high-cost flag using NTILE.

CREATE TABLE IF NOT EXISTS marts.mart_member_utilization (
    analytics_member_key  bigint PRIMARY KEY,
    plan_type             text NOT NULL,
    gender                text NOT NULL,
    birth_year             integer NOT NULL,
    claim_count            integer NOT NULL,
    total_billed            numeric(14, 2) NOT NULL,
    total_paid               numeric(14, 2) NOT NULL,
    cost_percentile          integer NOT NULL,
    is_high_cost             boolean NOT NULL,
    coverage_status          text
);

TRUNCATE marts.mart_member_utilization;

WITH member_claims AS (
    SELECT
        dm.analytics_member_key,
        dm.plan_type,
        dm.gender,
        dm.birth_year,
        count(fc.analytics_claim_key)     AS claim_count,
        COALESCE(sum(fc.billed_amount), 0) AS total_billed,
        COALESCE(sum(fc.paid_amount), 0)    AS total_paid
    FROM warehouse.dim_member dm
    LEFT JOIN warehouse.fact_claim fc ON fc.analytics_member_key = dm.analytics_member_key
    WHERE dm.is_current
    GROUP BY 1, 2, 3, 4
),
ranked AS (
    SELECT
        *,
        NTILE(100) OVER (ORDER BY total_paid) AS cost_percentile
    FROM member_claims
),
latest_coverage AS (
    SELECT DISTINCT ON (analytics_member_key)
        analytics_member_key, status
    FROM warehouse.fact_eligibility_coverage
    ORDER BY analytics_member_key, coverage_start DESC
)
INSERT INTO marts.mart_member_utilization (
    analytics_member_key, plan_type, gender, birth_year, claim_count, total_billed,
    total_paid, cost_percentile, is_high_cost, coverage_status
)
SELECT
    r.analytics_member_key,
    r.plan_type,
    r.gender,
    r.birth_year,
    r.claim_count,
    r.total_billed,
    r.total_paid,
    r.cost_percentile,
    r.cost_percentile >= 90 AS is_high_cost,
    lc.status
FROM ranked r
LEFT JOIN latest_coverage lc ON lc.analytics_member_key = r.analytics_member_key
ORDER BY r.total_paid DESC;
