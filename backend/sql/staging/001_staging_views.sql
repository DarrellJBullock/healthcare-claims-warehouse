-- Staging layer: light typing/cleaning views over raw.
-- No business aggregation happens here, only normalization:
--   * trims text
--   * drops obviously invalid rows (nulls in required business keys)
--   * standardizes casing for categorical fields

CREATE OR REPLACE VIEW staging.stg_members AS
SELECT
    trim(member_id)                AS member_id,
    trim(subscriber_id)            AS subscriber_id,
    trim(first_name)               AS first_name,
    trim(last_name)                AS last_name,
    date_of_birth,
    initcap(trim(gender))          AS gender,
    trim(address)                  AS address,
    trim(phone)                    AS phone,
    lower(trim(email))             AS email,
    initcap(trim(plan_type))       AS plan_type,
    effective_date,
    term_date,
    created_at
FROM raw.raw_members
WHERE member_id IS NOT NULL;

CREATE OR REPLACE VIEW staging.stg_providers AS
SELECT
    trim(provider_id)              AS provider_id,
    trim(provider_name)            AS provider_name,
    initcap(trim(specialty))       AS specialty,
    trim(npi)                      AS npi,
    initcap(trim(network_status))  AS network_status,
    trim(address)                  AS address,
    trim(phone)                    AS phone,
    created_at
FROM raw.raw_providers
WHERE provider_id IS NOT NULL;

CREATE OR REPLACE VIEW staging.stg_payers AS
SELECT
    trim(payer_id)                  AS payer_id,
    trim(payer_name)                AS payer_name,
    initcap(trim(payer_type))       AS payer_type,
    created_at
FROM raw.raw_payers
WHERE payer_id IS NOT NULL;

CREATE OR REPLACE VIEW staging.stg_denial_codes AS
SELECT
    trim(denial_code)      AS denial_code,
    trim(denial_reason)    AS denial_reason,
    initcap(trim(denial_category)) AS denial_category
FROM raw.raw_denial_codes
WHERE denial_code IS NOT NULL;

CREATE OR REPLACE VIEW staging.stg_claims AS
SELECT
    trim(claim_id)                  AS claim_id,
    trim(member_id)                 AS member_id,
    trim(provider_id)               AS provider_id,
    trim(payer_id)                  AS payer_id,
    initcap(trim(claim_type))       AS claim_type,
    initcap(trim(claim_status))     AS claim_status,
    diagnosis_category_code,
    denial_code,
    service_date_start,
    service_date_end,
    submitted_date,
    billed_amount,
    GREATEST(paid_amount, 0)        AS paid_amount,
    created_at
FROM raw.raw_claims
WHERE claim_id IS NOT NULL
  AND service_date_start IS NOT NULL
  AND billed_amount IS NOT NULL;

CREATE OR REPLACE VIEW staging.stg_claim_service_lines AS
SELECT
    trim(service_line_id)  AS service_line_id,
    trim(claim_id)         AS claim_id,
    line_number,
    procedure_category_code,
    service_date,
    GREATEST(units, 1)     AS units,
    billed_amount,
    allowed_amount,
    GREATEST(paid_amount, 0) AS paid_amount,
    created_at
FROM raw.raw_claim_service_lines
WHERE service_line_id IS NOT NULL
  AND claim_id IS NOT NULL;

CREATE OR REPLACE VIEW staging.stg_payments AS
SELECT
    trim(payment_id)        AS payment_id,
    trim(claim_id)          AS claim_id,
    payment_date,
    payment_amount,
    initcap(trim(payment_method)) AS payment_method,
    created_at
FROM raw.raw_payments
WHERE payment_id IS NOT NULL
  AND claim_id IS NOT NULL;

CREATE OR REPLACE VIEW staging.stg_adjustments AS
SELECT
    trim(adjustment_id)     AS adjustment_id,
    trim(claim_id)          AS claim_id,
    initcap(trim(adjustment_type)) AS adjustment_type,
    adjustment_amount,
    adjustment_date,
    reason_code,
    created_at
FROM raw.raw_adjustments
WHERE adjustment_id IS NOT NULL
  AND claim_id IS NOT NULL;

CREATE OR REPLACE VIEW staging.stg_eligibility AS
SELECT
    trim(eligibility_id)    AS eligibility_id,
    trim(member_id)         AS member_id,
    coverage_start,
    coverage_end,
    initcap(trim(plan_type)) AS plan_type,
    initcap(trim(status))    AS status,
    created_at
FROM raw.raw_eligibility
WHERE eligibility_id IS NOT NULL
  AND member_id IS NOT NULL;
