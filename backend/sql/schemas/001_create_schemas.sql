-- Healthcare Claims Analytics Warehouse
-- Synthetic data only. No real PHI is used in this portfolio project.
--
-- Creates the six logical schemas used across the warehouse:
--   raw          source-shaped synthetic tables (Django-managed)
--   staging      light cleaning/typing views over raw
--   warehouse    dimensional model (dims + facts)
--   marts        analytics-ready aggregate tables
--   audit        audit_events (Django-managed)
--   compliance   data_quality_results (Django-managed) + demo settings

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS warehouse;
CREATE SCHEMA IF NOT EXISTS marts;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS compliance;
