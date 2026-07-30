-- Mart: monthly claims summary (feeds dashboard summary + claims trend chart)

CREATE TABLE IF NOT EXISTS marts.mart_claims_summary (
    month_date       date PRIMARY KEY,
    total_claims     integer NOT NULL,
    total_billed     numeric(14, 2) NOT NULL,
    total_paid       numeric(14, 2) NOT NULL,
    denied_claims    integer NOT NULL,
    denial_rate      numeric(6, 4) NOT NULL,
    avg_paid_amount  numeric(12, 2) NOT NULL
);

TRUNCATE marts.mart_claims_summary;

WITH monthly AS (
    SELECT
        date_trunc('month', service_date_start)::date AS month_date,
        count(*)                                        AS total_claims,
        sum(billed_amount)                               AS total_billed,
        sum(paid_amount)                                  AS total_paid,
        sum(CASE WHEN is_denied THEN 1 ELSE 0 END)        AS denied_claims
    FROM warehouse.fact_claim
    GROUP BY 1
)
INSERT INTO marts.mart_claims_summary (
    month_date, total_claims, total_billed, total_paid, denied_claims, denial_rate, avg_paid_amount
)
SELECT
    month_date,
    total_claims,
    total_billed,
    total_paid,
    denied_claims,
    ROUND(denied_claims::numeric / NULLIF(total_claims, 0), 4)   AS denial_rate,
    ROUND(total_paid / NULLIF(total_claims, 0), 2)                AS avg_paid_amount
FROM monthly
ORDER BY month_date;
