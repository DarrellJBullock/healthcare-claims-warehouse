-- Data quality checks.
-- Each check is a self-contained SELECT returning failed_count and a
-- sample_record_key. Parsed and executed by the run_quality_checks
-- management command (apps/warehouse/management/commands/run_quality_checks.py),
-- which writes one row per check into compliance.data_quality_results.
--
-- Block header format (parsed by the command):
-- -- CHECK: <check_name> | TABLE: <table_name> | SEVERITY: <HIGH|MEDIUM|LOW> | MESSAGE: <message>

-- CHECK: required_claim_fields | TABLE: raw_claims | SEVERITY: HIGH | MESSAGE: Claims missing required fields (member, provider, payer, or billed amount)
SELECT count(*) AS failed_count, max(claim_id) AS sample_record_key
FROM raw.raw_claims
WHERE member_id IS NULL OR provider_id IS NULL OR payer_id IS NULL OR billed_amount IS NULL;

-- CHECK: required_member_fields | TABLE: raw_members | SEVERITY: HIGH | MESSAGE: Members missing required demographic fields
SELECT count(*) AS failed_count, max(member_id) AS sample_record_key
FROM raw.raw_members
WHERE first_name IS NULL OR last_name IS NULL OR date_of_birth IS NULL;

-- CHECK: duplicate_claim_ids | TABLE: raw_claims | SEVERITY: HIGH | MESSAGE: Duplicate claim_id values found
SELECT count(*) AS failed_count, max(claim_id) AS sample_record_key
FROM (
    SELECT claim_id FROM raw.raw_claims GROUP BY claim_id HAVING count(*) > 1
) dupes;

-- CHECK: duplicate_member_ids | TABLE: raw_members | SEVERITY: HIGH | MESSAGE: Duplicate member_id values found
SELECT count(*) AS failed_count, max(member_id) AS sample_record_key
FROM (
    SELECT member_id FROM raw.raw_members GROUP BY member_id HAVING count(*) > 1
) dupes;

-- CHECK: claim_service_line_amount_mismatch | TABLE: raw_claim_service_lines | SEVERITY: MEDIUM | MESSAGE: Sum of service line billed amounts does not match claim billed amount
SELECT count(*) AS failed_count, max(c.claim_id) AS sample_record_key
FROM raw.raw_claims c
JOIN (
    SELECT claim_id, sum(billed_amount) AS line_total
    FROM raw.raw_claim_service_lines
    GROUP BY claim_id
) sl ON sl.claim_id = c.claim_id
WHERE abs(c.billed_amount - sl.line_total) > 1.00;

-- CHECK: paid_amount_exceeds_billed | TABLE: raw_claims | SEVERITY: HIGH | MESSAGE: Paid amount is greater than billed amount
SELECT count(*) AS failed_count, max(claim_id) AS sample_record_key
FROM raw.raw_claims
WHERE paid_amount > billed_amount;

-- CHECK: missing_payer | TABLE: raw_claims | SEVERITY: HIGH | MESSAGE: Claims reference a payer_id not present in raw_payers
SELECT count(*) AS failed_count, max(c.claim_id) AS sample_record_key
FROM raw.raw_claims c
LEFT JOIN raw.raw_payers p ON p.payer_id = c.payer_id
WHERE p.payer_id IS NULL;

-- CHECK: missing_provider | TABLE: raw_claims | SEVERITY: HIGH | MESSAGE: Claims reference a provider_id not present in raw_providers
SELECT count(*) AS failed_count, max(c.claim_id) AS sample_record_key
FROM raw.raw_claims c
LEFT JOIN raw.raw_providers pr ON pr.provider_id = c.provider_id
WHERE pr.provider_id IS NULL;

-- CHECK: invalid_claim_dates | TABLE: raw_claims | SEVERITY: MEDIUM | MESSAGE: Claim service_date_end occurs before service_date_start
SELECT count(*) AS failed_count, max(claim_id) AS sample_record_key
FROM raw.raw_claims
WHERE service_date_end < service_date_start;

-- CHECK: service_date_after_payment_date | TABLE: raw_payments | SEVERITY: MEDIUM | MESSAGE: Payment posted before the claim's service date
SELECT count(*) AS failed_count, max(p.payment_id) AS sample_record_key
FROM raw.raw_payments p
JOIN raw.raw_claims c ON c.claim_id = p.claim_id
WHERE p.payment_date < c.service_date_start;

-- CHECK: member_coverage_gap | TABLE: raw_eligibility | SEVERITY: LOW | MESSAGE: Member has a coverage gap between eligibility periods
SELECT count(*) AS failed_count, max(member_id) AS sample_record_key
FROM (
    SELECT
        member_id,
        coverage_start,
        LAG(coverage_end) OVER (PARTITION BY member_id ORDER BY coverage_start) AS prior_coverage_end
    FROM raw.raw_eligibility
) gaps
WHERE prior_coverage_end IS NOT NULL AND coverage_start > prior_coverage_end + 1;

-- CHECK: orphan_service_lines | TABLE: raw_claim_service_lines | SEVERITY: HIGH | MESSAGE: Service lines reference a claim_id not present in raw_claims
SELECT count(*) AS failed_count, max(sl.service_line_id) AS sample_record_key
FROM raw.raw_claim_service_lines sl
LEFT JOIN raw.raw_claims c ON c.claim_id = sl.claim_id
WHERE c.claim_id IS NULL;

-- CHECK: orphan_adjustments | TABLE: raw_adjustments | SEVERITY: HIGH | MESSAGE: Adjustments reference a claim_id not present in raw_claims
SELECT count(*) AS failed_count, max(a.adjustment_id) AS sample_record_key
FROM raw.raw_adjustments a
LEFT JOIN raw.raw_claims c ON c.claim_id = a.claim_id
WHERE c.claim_id IS NULL;

-- CHECK: invalid_denial_code | TABLE: raw_claims | SEVERITY: MEDIUM | MESSAGE: Claim denial_code not present in raw_denial_codes
SELECT count(*) AS failed_count, max(c.claim_id) AS sample_record_key
FROM raw.raw_claims c
LEFT JOIN raw.raw_denial_codes d ON d.denial_code = c.denial_code
WHERE c.denial_code IS NOT NULL AND d.denial_code IS NULL;

-- CHECK: invalid_claim_status | TABLE: raw_claims | SEVERITY: MEDIUM | MESSAGE: Claim status is not one of the recognized values
SELECT count(*) AS failed_count, max(claim_id) AS sample_record_key
FROM raw.raw_claims
WHERE initcap(trim(claim_status)) NOT IN ('Paid', 'Denied', 'Pending', 'Partially Paid');
