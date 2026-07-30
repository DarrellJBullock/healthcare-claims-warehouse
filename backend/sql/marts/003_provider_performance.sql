-- Mart: provider performance ranking.

CREATE TABLE IF NOT EXISTS marts.mart_provider_performance (
    analytics_provider_key  bigint PRIMARY KEY,
    provider_name           text NOT NULL,
    specialty               text NOT NULL,
    network_status          text NOT NULL,
    total_claims            integer NOT NULL,
    total_billed            numeric(14, 2) NOT NULL,
    total_paid              numeric(14, 2) NOT NULL,
    denial_rate             numeric(6, 4) NOT NULL,
    avg_reimbursement       numeric(12, 2) NOT NULL,
    top_procedure_category  text,
    paid_rank               integer NOT NULL,
    is_high_risk            boolean NOT NULL
);

TRUNCATE marts.mart_provider_performance;

WITH provider_claims AS (
    SELECT
        dp.analytics_provider_key,
        dp.provider_name,
        dp.specialty,
        dp.network_status,
        count(*)                                    AS total_claims,
        sum(fc.billed_amount)                        AS total_billed,
        sum(fc.paid_amount)                           AS total_paid,
        sum(CASE WHEN fc.is_denied THEN 1 ELSE 0 END) AS denied_claims
    FROM warehouse.fact_claim fc
    JOIN warehouse.dim_provider dp ON dp.analytics_provider_key = fc.analytics_provider_key
    GROUP BY 1, 2, 3, 4
),
top_procedure AS (
    SELECT analytics_provider_key, procedure_category_code
    FROM (
        SELECT
            fc.analytics_provider_key,
            pc.procedure_category_name AS procedure_category_code,
            ROW_NUMBER() OVER (
                PARTITION BY fc.analytics_provider_key
                ORDER BY count(*) DESC
            ) AS rn
        FROM warehouse.fact_claim_service_line sl
        JOIN warehouse.fact_claim fc ON fc.analytics_claim_key = sl.analytics_claim_key
        JOIN warehouse.dim_procedure_category pc ON pc.procedure_category_code = sl.procedure_category_code
        GROUP BY fc.analytics_provider_key, pc.procedure_category_name
    ) ranked
    WHERE rn = 1
)
INSERT INTO marts.mart_provider_performance (
    analytics_provider_key, provider_name, specialty, network_status, total_claims,
    total_billed, total_paid, denial_rate, avg_reimbursement, top_procedure_category,
    paid_rank, is_high_risk
)
SELECT
    pc.analytics_provider_key,
    pc.provider_name,
    pc.specialty,
    pc.network_status,
    pc.total_claims,
    pc.total_billed,
    pc.total_paid,
    ROUND(pc.denied_claims::numeric / NULLIF(pc.total_claims, 0), 4) AS denial_rate,
    ROUND(pc.total_paid / NULLIF(pc.total_claims, 0), 2)              AS avg_reimbursement,
    tp.procedure_category_code,
    RANK() OVER (ORDER BY pc.total_paid DESC)                        AS paid_rank,
    (pc.denied_claims::numeric / NULLIF(pc.total_claims, 0)) > 0.25   AS is_high_risk
FROM provider_claims pc
LEFT JOIN top_procedure tp ON tp.analytics_provider_key = pc.analytics_provider_key
ORDER BY paid_rank;
