-- Mart: payer performance ranking, including average days-to-pay and
-- adjustment trend.

CREATE TABLE IF NOT EXISTS marts.mart_payer_performance (
    analytics_payer_key  bigint PRIMARY KEY,
    payer_name           text NOT NULL,
    payer_type           text NOT NULL,
    total_claims         integer NOT NULL,
    total_billed         numeric(14, 2) NOT NULL,
    total_paid           numeric(14, 2) NOT NULL,
    denial_rate          numeric(6, 4) NOT NULL,
    avg_days_to_pay      numeric(6, 2),
    total_adjustments    numeric(14, 2) NOT NULL,
    paid_rank            integer NOT NULL
);

TRUNCATE marts.mart_payer_performance;

WITH payer_claims AS (
    SELECT
        dpay.analytics_payer_key,
        dpay.payer_name,
        dpay.payer_type,
        count(*)                                      AS total_claims,
        sum(fc.billed_amount)                          AS total_billed,
        sum(fc.paid_amount)                             AS total_paid,
        sum(CASE WHEN fc.is_denied THEN 1 ELSE 0 END)   AS denied_claims
    FROM warehouse.fact_claim fc
    JOIN warehouse.dim_payer dpay ON dpay.analytics_payer_key = fc.analytics_payer_key
    GROUP BY 1, 2, 3
),
payment_speed AS (
    SELECT fc.analytics_payer_key, avg(fp.days_to_pay) AS avg_days_to_pay
    FROM warehouse.fact_payment fp
    JOIN warehouse.fact_claim fc ON fc.analytics_claim_key = fp.analytics_claim_key
    GROUP BY fc.analytics_payer_key
),
adjustments AS (
    SELECT fc.analytics_payer_key, sum(fa.adjustment_amount) AS total_adjustments
    FROM warehouse.fact_adjustment fa
    JOIN warehouse.fact_claim fc ON fc.analytics_claim_key = fa.analytics_claim_key
    GROUP BY fc.analytics_payer_key
)
INSERT INTO marts.mart_payer_performance (
    analytics_payer_key, payer_name, payer_type, total_claims, total_billed, total_paid,
    denial_rate, avg_days_to_pay, total_adjustments, paid_rank
)
SELECT
    pc.analytics_payer_key,
    pc.payer_name,
    pc.payer_type,
    pc.total_claims,
    pc.total_billed,
    pc.total_paid,
    ROUND(pc.denied_claims::numeric / NULLIF(pc.total_claims, 0), 4) AS denial_rate,
    ROUND(ps.avg_days_to_pay, 2),
    COALESCE(adj.total_adjustments, 0),
    RANK() OVER (ORDER BY pc.total_paid DESC) AS paid_rank
FROM payer_claims pc
LEFT JOIN payment_speed ps ON ps.analytics_payer_key = pc.analytics_payer_key
LEFT JOIN adjustments adj ON adj.analytics_payer_key = pc.analytics_payer_key
ORDER BY paid_rank;
