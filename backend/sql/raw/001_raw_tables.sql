-- Raw layer: source-system-shaped synthetic tables.
-- These tables are created and populated by Django (apps/warehouse/models.py
-- + the seed_synthetic_claims management command). This file documents the
-- exact shape of the raw layer for SQL-first review and is safe to re-run
-- (CREATE TABLE IF NOT EXISTS) if you want to provision the schema by hand.
--
-- Synthetic identifiers only, e.g. MBR-10039281, CLM-2026-000938, PRV-20381.
-- No real patient names, addresses, or PHI.

CREATE TABLE IF NOT EXISTS raw.raw_members (
    member_id       text PRIMARY KEY,
    subscriber_id   text NOT NULL,
    first_name      text NOT NULL,
    last_name       text NOT NULL,
    date_of_birth   date NOT NULL,
    gender          text NOT NULL,
    address         text NOT NULL,
    phone           text NOT NULL,
    email           text NOT NULL,
    plan_type       text NOT NULL,
    effective_date  date NOT NULL,
    term_date       date,
    created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw.raw_providers (
    provider_id     text PRIMARY KEY,
    provider_name   text NOT NULL,
    specialty       text NOT NULL,
    npi             text NOT NULL,
    network_status  text NOT NULL,
    address         text NOT NULL,
    phone           text NOT NULL,
    created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw.raw_payers (
    payer_id        text PRIMARY KEY,
    payer_name      text NOT NULL,
    payer_type      text NOT NULL,
    created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw.raw_diagnosis_categories (
    diagnosis_category_code text PRIMARY KEY,
    diagnosis_category_name text NOT NULL
);

CREATE TABLE IF NOT EXISTS raw.raw_procedure_categories (
    procedure_category_code text PRIMARY KEY,
    procedure_category_name text NOT NULL
);

CREATE TABLE IF NOT EXISTS raw.raw_denial_codes (
    denial_code     text PRIMARY KEY,
    denial_reason   text NOT NULL,
    denial_category text NOT NULL
);

CREATE TABLE IF NOT EXISTS raw.raw_claims (
    claim_id                 text PRIMARY KEY,
    member_id                text NOT NULL REFERENCES raw.raw_members(member_id),
    provider_id              text NOT NULL REFERENCES raw.raw_providers(provider_id),
    payer_id                 text NOT NULL REFERENCES raw.raw_payers(payer_id),
    claim_type               text NOT NULL,
    claim_status             text NOT NULL,
    diagnosis_category_code  text REFERENCES raw.raw_diagnosis_categories(diagnosis_category_code),
    denial_code              text REFERENCES raw.raw_denial_codes(denial_code),
    service_date_start       date NOT NULL,
    service_date_end         date NOT NULL,
    submitted_date           date NOT NULL,
    billed_amount            numeric(12, 2) NOT NULL,
    paid_amount              numeric(12, 2) NOT NULL DEFAULT 0,
    created_at               timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw.raw_claim_service_lines (
    service_line_id          text PRIMARY KEY,
    claim_id                 text NOT NULL REFERENCES raw.raw_claims(claim_id),
    line_number              integer NOT NULL,
    procedure_category_code  text REFERENCES raw.raw_procedure_categories(procedure_category_code),
    service_date             date NOT NULL,
    units                    integer NOT NULL DEFAULT 1,
    billed_amount            numeric(12, 2) NOT NULL,
    allowed_amount           numeric(12, 2) NOT NULL DEFAULT 0,
    paid_amount              numeric(12, 2) NOT NULL DEFAULT 0,
    created_at               timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw.raw_payments (
    payment_id      text PRIMARY KEY,
    claim_id        text NOT NULL REFERENCES raw.raw_claims(claim_id),
    payment_date    date NOT NULL,
    payment_amount  numeric(12, 2) NOT NULL,
    payment_method  text NOT NULL,
    created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw.raw_adjustments (
    adjustment_id     text PRIMARY KEY,
    claim_id          text NOT NULL REFERENCES raw.raw_claims(claim_id),
    adjustment_type   text NOT NULL,
    adjustment_amount numeric(12, 2) NOT NULL,
    adjustment_date   date NOT NULL,
    reason_code       text,
    created_at        timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw.raw_eligibility (
    eligibility_id  text PRIMARY KEY,
    member_id       text NOT NULL REFERENCES raw.raw_members(member_id),
    coverage_start  date NOT NULL,
    coverage_end    date,
    plan_type       text NOT NULL,
    status          text NOT NULL,
    created_at      timestamptz NOT NULL DEFAULT now()
);
