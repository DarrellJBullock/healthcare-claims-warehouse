-- Mart: monthly KPI trend with month-over-month growth via LAG().

CREATE TABLE IF NOT EXISTS marts.mart_monthly_claims_kpis (
    month_date            date PRIMARY KEY,
    total_claims          integer NOT NULL,
    total_billed          numeric(14, 2) NOT NULL,
    total_paid            numeric(14, 2) NOT NULL,
    denial_rate           numeric(6, 4) NOT NULL,
    avg_days_to_pay       numeric(6, 2),
    claims_mom_growth     numeric(6, 4),
    paid_amount_mom_growth numeric(6, 4)
);

TRUNCATE marts.mart_monthly_claims_kpis;

WITH monthly AS (
    SELECT
        date_trunc('month', fc.service_date_start)::date AS month_date,
        count(*)                                           AS total_claims,
        sum(fc.billed_amount)                              AS total_billed,
        sum(fc.paid_amount)                                 AS total_paid,
        sum(CASE WHEN fc.is_denied THEN 1 ELSE 0 END)       AS denied_claims
    FROM warehouse.fact_claim fc
    GROUP BY 1
),
pay_speed AS (
    SELECT
        date_trunc('month', fc.service_date_start)::date AS month_date,
        avg(fp.days_to_pay) AS avg_days_to_pay
    FROM warehouse.fact_payment fp
    JOIN warehouse.fact_claim fc ON fc.analytics_claim_key = fp.analytics_claim_key
    GROUP BY 1
),
combined AS (
    SELECT
        m.month_date,
        m.total_claims,
        m.total_billed,
        m.total_paid,
        ROUND(m.denied_claims::numeric / NULLIF(m.total_claims, 0), 4) AS denial_rate,
        ROUND(ps.avg_days_to_pay, 2) AS avg_days_to_pay
    FROM monthly m
    LEFT JOIN pay_speed ps ON ps.month_date = m.month_date
)
INSERT INTO marts.mart_monthly_claims_kpis (
    month_date, total_claims, total_billed, total_paid, denial_rate, avg_days_to_pay,
    claims_mom_growth, paid_amount_mom_growth
)
SELECT
    month_date,
    total_claims,
    total_billed,
    total_paid,
    denial_rate,
    avg_days_to_pay,
    ROUND(
        (total_claims - LAG(total_claims) OVER (ORDER BY month_date))::numeric
            / NULLIF(LAG(total_claims) OVER (ORDER BY month_date), 0),
        4
    ) AS claims_mom_growth,
    ROUND(
        (total_paid - LAG(total_paid) OVER (ORDER BY month_date))
            / NULLIF(LAG(total_paid) OVER (ORDER BY month_date), 0),
        4
    ) AS paid_amount_mom_growth
FROM combined
ORDER BY month_date;
