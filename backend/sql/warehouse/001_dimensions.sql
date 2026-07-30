-- Warehouse dimensions.
-- Surrogate analytics_*_key columns are the only keys marts are allowed to
-- join on; raw business identifiers (member_id, claim_id, ...) never leave
-- this layer un-masked into the API/frontend.

CREATE TABLE IF NOT EXISTS warehouse.dim_date (
    date_key        integer PRIMARY KEY,
    full_date       date NOT NULL UNIQUE,
    year            integer NOT NULL,
    quarter         integer NOT NULL,
    month           integer NOT NULL,
    month_name      text NOT NULL,
    day             integer NOT NULL,
    day_of_week     integer NOT NULL,
    day_name        text NOT NULL,
    is_weekend      boolean NOT NULL
);

-- SCD Type 2 dimension: tracks member plan/demographic changes over time.
CREATE TABLE IF NOT EXISTS warehouse.dim_member (
    analytics_member_key  bigserial PRIMARY KEY,
    member_id             text NOT NULL,
    gender                text NOT NULL,
    birth_year             integer NOT NULL,
    plan_type             text NOT NULL,
    row_hash              text NOT NULL,
    valid_from             timestamptz NOT NULL DEFAULT now(),
    valid_to               timestamptz,
    is_current             boolean NOT NULL DEFAULT true
);

CREATE INDEX IF NOT EXISTS idx_dim_member_business_key
    ON warehouse.dim_member (member_id, is_current);

-- Type 1 dimension: providers (current-state only for this portfolio demo).
CREATE TABLE IF NOT EXISTS warehouse.dim_provider (
    analytics_provider_key  bigserial PRIMARY KEY,
    provider_id             text NOT NULL UNIQUE,
    provider_name           text NOT NULL,
    specialty               text NOT NULL,
    network_status          text NOT NULL
);

CREATE TABLE IF NOT EXISTS warehouse.dim_payer (
    analytics_payer_key  bigserial PRIMARY KEY,
    payer_id             text NOT NULL UNIQUE,
    payer_name           text NOT NULL,
    payer_type           text NOT NULL
);

CREATE TABLE IF NOT EXISTS warehouse.dim_diagnosis_category (
    diagnosis_category_code text PRIMARY KEY,
    diagnosis_category_name text NOT NULL
);

CREATE TABLE IF NOT EXISTS warehouse.dim_procedure_category (
    procedure_category_code text PRIMARY KEY,
    procedure_category_name text NOT NULL
);

CREATE TABLE IF NOT EXISTS warehouse.dim_denial_reason (
    denial_code     text PRIMARY KEY,
    denial_reason   text NOT NULL,
    denial_category text NOT NULL
);

-- ---------------------------------------------------------------------
-- Load: dim_date (idempotent, regenerates a 6-year synthetic date range)
-- ---------------------------------------------------------------------
INSERT INTO warehouse.dim_date (
    date_key, full_date, year, quarter, month, month_name, day, day_of_week, day_name, is_weekend
)
SELECT
    to_char(d, 'YYYYMMDD')::int,
    d,
    extract(year FROM d)::int,
    extract(quarter FROM d)::int,
    extract(month FROM d)::int,
    to_char(d, 'Month'),
    extract(day FROM d)::int,
    extract(dow FROM d)::int,
    to_char(d, 'Day'),
    extract(dow FROM d) IN (0, 6)
FROM generate_series('2023-01-01'::date, '2027-12-31'::date, interval '1 day') AS d
ON CONFLICT (date_key) DO NOTHING;

-- ---------------------------------------------------------------------
-- Load: dim_provider / dim_payer / category & denial reference dims
-- (type 1 — truncate and reload from staging on every build_marts run)
-- ---------------------------------------------------------------------
-- CASCADE is required (and safe) here: warehouse.fact_claim references
-- these dims by FK, and fact_claim is itself fully truncated and reloaded
-- by warehouse/002_facts.sql immediately after this file runs.
TRUNCATE warehouse.dim_provider CASCADE;
INSERT INTO warehouse.dim_provider (provider_id, provider_name, specialty, network_status)
SELECT provider_id, provider_name, specialty, network_status
FROM staging.stg_providers;

TRUNCATE warehouse.dim_payer CASCADE;
INSERT INTO warehouse.dim_payer (payer_id, payer_name, payer_type)
SELECT payer_id, payer_name, payer_type
FROM staging.stg_payers;

TRUNCATE warehouse.dim_diagnosis_category CASCADE;
INSERT INTO warehouse.dim_diagnosis_category
SELECT diagnosis_category_code, diagnosis_category_name
FROM raw.raw_diagnosis_categories;

TRUNCATE warehouse.dim_procedure_category CASCADE;
INSERT INTO warehouse.dim_procedure_category
SELECT procedure_category_code, procedure_category_name
FROM raw.raw_procedure_categories;

TRUNCATE warehouse.dim_denial_reason CASCADE;
INSERT INTO warehouse.dim_denial_reason
SELECT denial_code, denial_reason, denial_category
FROM staging.stg_denial_codes;

-- ---------------------------------------------------------------------
-- Load: dim_member (SCD Type 2)
-- Step 1: expire current rows whose tracked attributes changed.
-- Step 2: insert new rows for brand-new members or changed members.
-- ---------------------------------------------------------------------
WITH incoming AS (
    SELECT
        member_id,
        gender,
        extract(year FROM date_of_birth)::int AS birth_year,
        plan_type,
        md5(gender || '|' || extract(year FROM date_of_birth)::text || '|' || plan_type) AS row_hash
    FROM staging.stg_members
),
changed AS (
    SELECT i.member_id
    FROM incoming i
    JOIN warehouse.dim_member d
        ON d.member_id = i.member_id AND d.is_current
    WHERE d.row_hash <> i.row_hash
)
UPDATE warehouse.dim_member d
SET is_current = false,
    valid_to = now()
FROM changed c
WHERE d.member_id = c.member_id
  AND d.is_current;

WITH incoming AS (
    SELECT
        member_id,
        gender,
        extract(year FROM date_of_birth)::int AS birth_year,
        plan_type,
        md5(gender || '|' || extract(year FROM date_of_birth)::text || '|' || plan_type) AS row_hash
    FROM staging.stg_members
)
INSERT INTO warehouse.dim_member (member_id, gender, birth_year, plan_type, row_hash, valid_from, is_current)
SELECT i.member_id, i.gender, i.birth_year, i.plan_type, i.row_hash, now(), true
FROM incoming i
LEFT JOIN warehouse.dim_member d
    ON d.member_id = i.member_id AND d.is_current
WHERE d.analytics_member_key IS NULL;
