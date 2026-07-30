-- Warehouse facts.
-- Built as truncate-and-reload tables (typical for a demo-scale synthetic
-- warehouse) joining staging views to dimension surrogate keys. Business
-- identifiers (claim_id, member_id) are retained only as attributes needed
-- to join back for masked display -- marts should prefer analytics_*_key.

CREATE TABLE IF NOT EXISTS warehouse.fact_claim (
    analytics_claim_key     bigserial PRIMARY KEY,
    claim_id                text NOT NULL UNIQUE,
    analytics_member_key    bigint REFERENCES warehouse.dim_member(analytics_member_key),
    analytics_provider_key  bigint REFERENCES warehouse.dim_provider(analytics_provider_key),
    analytics_payer_key     bigint REFERENCES warehouse.dim_payer(analytics_payer_key),
    diagnosis_category_code text REFERENCES warehouse.dim_diagnosis_category(diagnosis_category_code),
    denial_code             text REFERENCES warehouse.dim_denial_reason(denial_code),
    service_date_key        integer REFERENCES warehouse.dim_date(date_key),
    claim_type              text NOT NULL,
    claim_status            text NOT NULL,
    service_date_start      date NOT NULL,
    service_date_end        date NOT NULL,
    submitted_date           date NOT NULL,
    billed_amount            numeric(12, 2) NOT NULL,
    paid_amount              numeric(12, 2) NOT NULL,
    is_denied                boolean NOT NULL,
    days_to_submit           integer NOT NULL
);

CREATE TABLE IF NOT EXISTS warehouse.fact_claim_service_line (
    analytics_service_line_key bigserial PRIMARY KEY,
    analytics_claim_key        bigint REFERENCES warehouse.fact_claim(analytics_claim_key),
    procedure_category_code    text REFERENCES warehouse.dim_procedure_category(procedure_category_code),
    line_number                integer NOT NULL,
    service_date_key            integer REFERENCES warehouse.dim_date(date_key),
    units                        integer NOT NULL,
    billed_amount                numeric(12, 2) NOT NULL,
    allowed_amount                numeric(12, 2) NOT NULL,
    paid_amount                   numeric(12, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS warehouse.fact_payment (
    analytics_payment_key  bigserial PRIMARY KEY,
    analytics_claim_key    bigint REFERENCES warehouse.fact_claim(analytics_claim_key),
    payment_date_key        integer REFERENCES warehouse.dim_date(date_key),
    payment_date             date NOT NULL,
    payment_amount           numeric(12, 2) NOT NULL,
    payment_method           text NOT NULL,
    days_to_pay              integer NOT NULL
);

CREATE TABLE IF NOT EXISTS warehouse.fact_adjustment (
    analytics_adjustment_key bigserial PRIMARY KEY,
    analytics_claim_key      bigint REFERENCES warehouse.fact_claim(analytics_claim_key),
    adjustment_type           text NOT NULL,
    adjustment_amount          numeric(12, 2) NOT NULL,
    adjustment_date             date NOT NULL,
    reason_code                 text
);

CREATE TABLE IF NOT EXISTS warehouse.fact_eligibility_coverage (
    analytics_eligibility_key bigserial PRIMARY KEY,
    analytics_member_key      bigint REFERENCES warehouse.dim_member(analytics_member_key),
    coverage_start              date NOT NULL,
    coverage_end                 date,
    plan_type                    text NOT NULL,
    status                       text NOT NULL,
    gap_days_since_prior_coverage integer
);

-- ---------------------------------------------------------------------
-- Load: fact_claim
-- ---------------------------------------------------------------------
TRUNCATE warehouse.fact_claim CASCADE;

INSERT INTO warehouse.fact_claim (
    claim_id, analytics_member_key, analytics_provider_key, analytics_payer_key,
    diagnosis_category_code, denial_code, service_date_key, claim_type, claim_status,
    service_date_start, service_date_end, submitted_date, billed_amount, paid_amount,
    is_denied, days_to_submit
)
SELECT
    c.claim_id,
    dm.analytics_member_key,
    dp.analytics_provider_key,
    dpay.analytics_payer_key,
    c.diagnosis_category_code,
    c.denial_code,
    to_char(c.service_date_start, 'YYYYMMDD')::int,
    c.claim_type,
    c.claim_status,
    c.service_date_start,
    c.service_date_end,
    c.submitted_date,
    c.billed_amount,
    c.paid_amount,
    (c.claim_status = 'Denied'),
    GREATEST((c.submitted_date - c.service_date_start), 0)
FROM staging.stg_claims c
JOIN warehouse.dim_member dm ON dm.member_id = c.member_id AND dm.is_current
JOIN warehouse.dim_provider dp ON dp.provider_id = c.provider_id
JOIN warehouse.dim_payer dpay ON dpay.payer_id = c.payer_id;

-- ---------------------------------------------------------------------
-- Load: fact_claim_service_line
-- ---------------------------------------------------------------------
TRUNCATE warehouse.fact_claim_service_line;

INSERT INTO warehouse.fact_claim_service_line (
    analytics_claim_key, procedure_category_code, line_number, service_date_key,
    units, billed_amount, allowed_amount, paid_amount
)
SELECT
    fc.analytics_claim_key,
    sl.procedure_category_code,
    sl.line_number,
    to_char(sl.service_date, 'YYYYMMDD')::int,
    sl.units,
    sl.billed_amount,
    sl.allowed_amount,
    sl.paid_amount
FROM staging.stg_claim_service_lines sl
JOIN warehouse.fact_claim fc ON fc.claim_id = sl.claim_id;

-- ---------------------------------------------------------------------
-- Load: fact_payment (days_to_pay computed vs. claim submission date)
-- ---------------------------------------------------------------------
TRUNCATE warehouse.fact_payment;

INSERT INTO warehouse.fact_payment (
    analytics_claim_key, payment_date_key, payment_date, payment_amount, payment_method, days_to_pay
)
SELECT
    fc.analytics_claim_key,
    to_char(p.payment_date, 'YYYYMMDD')::int,
    p.payment_date,
    p.payment_amount,
    p.payment_method,
    GREATEST((p.payment_date - fc.submitted_date), 0)
FROM staging.stg_payments p
JOIN warehouse.fact_claim fc ON fc.claim_id = p.claim_id;

-- ---------------------------------------------------------------------
-- Load: fact_adjustment
-- ---------------------------------------------------------------------
TRUNCATE warehouse.fact_adjustment;

INSERT INTO warehouse.fact_adjustment (
    analytics_claim_key, adjustment_type, adjustment_amount, adjustment_date, reason_code
)
SELECT
    fc.analytics_claim_key,
    a.adjustment_type,
    a.adjustment_amount,
    a.adjustment_date,
    a.reason_code
FROM staging.stg_adjustments a
JOIN warehouse.fact_claim fc ON fc.claim_id = a.claim_id;

-- ---------------------------------------------------------------------
-- Load: fact_eligibility_coverage
-- gap_days_since_prior_coverage uses LAG() to detect coverage gaps per
-- member, a common member-utilization / eligibility data quality signal.
-- ---------------------------------------------------------------------
TRUNCATE warehouse.fact_eligibility_coverage;

INSERT INTO warehouse.fact_eligibility_coverage (
    analytics_member_key, coverage_start, coverage_end, plan_type, status, gap_days_since_prior_coverage
)
SELECT
    dm.analytics_member_key,
    e.coverage_start,
    e.coverage_end,
    e.plan_type,
    e.status,
    GREATEST(
        (e.coverage_start - LAG(e.coverage_end) OVER (
            PARTITION BY e.member_id ORDER BY e.coverage_start
        )),
        0
    )
FROM staging.stg_eligibility e
JOIN warehouse.dim_member dm ON dm.member_id = e.member_id AND dm.is_current;
