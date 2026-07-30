-- Mart: claim-level payment reconciliation.
-- Flags claims where paid_amount + total_adjustments materially diverges
-- from billed_amount, a common finance/ops reconciliation check.

CREATE TABLE IF NOT EXISTS marts.mart_payment_reconciliation (
    analytics_claim_key   bigint PRIMARY KEY,
    claim_status          text NOT NULL,
    billed_amount         numeric(12, 2) NOT NULL,
    paid_amount           numeric(12, 2) NOT NULL,
    total_adjustments     numeric(12, 2) NOT NULL,
    variance_amount       numeric(12, 2) NOT NULL,
    reconciliation_status text NOT NULL
);

TRUNCATE marts.mart_payment_reconciliation;

WITH adj AS (
    SELECT analytics_claim_key, sum(adjustment_amount) AS total_adjustments
    FROM warehouse.fact_adjustment
    GROUP BY 1
)
INSERT INTO marts.mart_payment_reconciliation (
    analytics_claim_key, claim_status, billed_amount, paid_amount, total_adjustments,
    variance_amount, reconciliation_status
)
SELECT
    fc.analytics_claim_key,
    fc.claim_status,
    fc.billed_amount,
    fc.paid_amount,
    COALESCE(a.total_adjustments, 0) AS total_adjustments,
    fc.billed_amount - (fc.paid_amount + COALESCE(a.total_adjustments, 0)) AS variance_amount,
    CASE
        WHEN fc.claim_status = 'Denied' THEN 'Denied - No Payment Expected'
        WHEN abs(fc.billed_amount - (fc.paid_amount + COALESCE(a.total_adjustments, 0))) <= 1.00
            THEN 'Reconciled'
        WHEN (fc.paid_amount + COALESCE(a.total_adjustments, 0)) > fc.billed_amount
            THEN 'Overpaid - Review'
        ELSE 'Variance - Review'
    END AS reconciliation_status
FROM warehouse.fact_claim fc
LEFT JOIN adj a ON a.analytics_claim_key = fc.analytics_claim_key;
