-- Mart: denial trends by month and reason, ranked by volume within month.

CREATE TABLE IF NOT EXISTS marts.mart_denial_trends (
    month_date      date NOT NULL,
    denial_code     text NOT NULL,
    denial_reason   text NOT NULL,
    denial_category text NOT NULL,
    denial_count    integer NOT NULL,
    denial_rate     numeric(6, 4) NOT NULL,
    rank_in_month   integer NOT NULL,
    PRIMARY KEY (month_date, denial_code)
);

TRUNCATE marts.mart_denial_trends;

WITH denied AS (
    SELECT
        date_trunc('month', fc.service_date_start)::date AS month_date,
        fc.denial_code,
        dr.denial_reason,
        dr.denial_category,
        count(*) AS denial_count
    FROM warehouse.fact_claim fc
    JOIN warehouse.dim_denial_reason dr ON dr.denial_code = fc.denial_code
    WHERE fc.is_denied
    GROUP BY 1, 2, 3, 4
),
month_totals AS (
    SELECT month_date, sum(denial_count) AS total_denials
    FROM denied
    GROUP BY 1
)
INSERT INTO marts.mart_denial_trends (
    month_date, denial_code, denial_reason, denial_category, denial_count, denial_rate, rank_in_month
)
SELECT
    d.month_date,
    d.denial_code,
    d.denial_reason,
    d.denial_category,
    d.denial_count,
    ROUND(d.denial_count::numeric / NULLIF(mt.total_denials, 0), 4) AS denial_rate,
    RANK() OVER (PARTITION BY d.month_date ORDER BY d.denial_count DESC) AS rank_in_month
FROM denied d
JOIN month_totals mt ON mt.month_date = d.month_date
ORDER BY d.month_date, rank_in_month;
