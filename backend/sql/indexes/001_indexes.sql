-- Indexes supporting the dashboard's most common analytical filters
-- (date range, payer, provider, claim status, denial reason).

CREATE INDEX IF NOT EXISTS idx_fact_claim_service_date ON warehouse.fact_claim (service_date_start);
CREATE INDEX IF NOT EXISTS idx_fact_claim_provider ON warehouse.fact_claim (analytics_provider_key);
CREATE INDEX IF NOT EXISTS idx_fact_claim_payer ON warehouse.fact_claim (analytics_payer_key);
CREATE INDEX IF NOT EXISTS idx_fact_claim_member ON warehouse.fact_claim (analytics_member_key);
CREATE INDEX IF NOT EXISTS idx_fact_claim_status ON warehouse.fact_claim (claim_status);
CREATE INDEX IF NOT EXISTS idx_fact_claim_denial ON warehouse.fact_claim (denial_code);

CREATE INDEX IF NOT EXISTS idx_fact_service_line_claim ON warehouse.fact_claim_service_line (analytics_claim_key);
CREATE INDEX IF NOT EXISTS idx_fact_payment_claim ON warehouse.fact_payment (analytics_claim_key);
CREATE INDEX IF NOT EXISTS idx_fact_adjustment_claim ON warehouse.fact_adjustment (analytics_claim_key);
CREATE INDEX IF NOT EXISTS idx_fact_eligibility_member ON warehouse.fact_eligibility_coverage (analytics_member_key);

CREATE INDEX IF NOT EXISTS idx_raw_claims_member ON raw.raw_claims (member_id);
CREATE INDEX IF NOT EXISTS idx_raw_claims_provider ON raw.raw_claims (provider_id);
CREATE INDEX IF NOT EXISTS idx_raw_claims_payer ON raw.raw_claims (payer_id);
CREATE INDEX IF NOT EXISTS idx_raw_service_lines_claim ON raw.raw_claim_service_lines (claim_id);
CREATE INDEX IF NOT EXISTS idx_raw_payments_claim ON raw.raw_payments (claim_id);
CREATE INDEX IF NOT EXISTS idx_raw_adjustments_claim ON raw.raw_adjustments (claim_id);
CREATE INDEX IF NOT EXISTS idx_raw_eligibility_member ON raw.raw_eligibility (member_id);
