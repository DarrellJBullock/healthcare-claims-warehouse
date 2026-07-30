# Healthcare Claims Analytics Warehouse, Claude Code Instructions

## Project

Project name:
healthcare-claims-warehouse

Build a production-style, HIPAA-aware healthcare claims analytics warehouse and dashboard using synthetic data only.

Portfolio angle:
Built a HIPAA-aware healthcare claims analytics warehouse using Python, Django, React, PostgreSQL, advanced SQL, role-based views, masked identifiers, audit logging, export controls, and data quality checks.

## Default Claude behavior

Do not ask clarifying questions unless blocked.
Make reasonable assumptions, document them, and continue building.
Batch any required questions into one list before coding.
Do not stop after planning.
Create the plan, then implement it.
Build a working MVP first, then polish.
Prefer progress over waiting for small decisions.
Use placeholders where details are missing.
Document placeholders clearly in the README and source comments.

## Compliance positioning

This project uses synthetic healthcare claims data only.
Do not use real PHI.
Do not claim certified HIPAA compliance.
Use the wording HIPAA-aware and compliance-minded engineering patterns.

The README and UI must clearly state:
Synthetic data only. No real PHI is used in this portfolio project.

A production deployment handling real ePHI would require legal review, risk analysis, Business Associate Agreements, secure hosting, organizational policies, staff training, monitoring, and operational safeguards.

## Tech stack

Use:
- Python
- Django
- Django REST Framework
- PostgreSQL
- Advanced SQL
- React
- TypeScript
- Tailwind CSS
- Vite
- Docker Compose
- Synthetic seed data
- Role-based demo views
- CSV export support

## Data engineering expectations

This must be SQL-first.

Use:
- raw schema
- staging schema
- warehouse schema
- marts schema
- audit schema
- compliance schema

Use advanced SQL:
- CTEs
- window functions
- aggregations
- date logic
- ranking
- case expressions
- joins
- data quality queries
- indexes
- views or materialized views where useful

Do not build only a CRUD app.
The dashboard should sit on top of warehouse-style SQL models.

## HIPAA-aware controls

Implement:
- synthetic data notice
- role-based demo views
- minimum necessary views
- masked identifiers
- surrogate analytics keys
- audit logging
- export controls
- retention policy demo
- safe logging
- no real PHI
- no committed secrets

Mask:
- member_id
- subscriber_id
- claim_id
- date_of_birth
- address
- phone
- email

Example:
MBR-10039281 becomes MBR-••••9281
CLM-2026-000938 becomes CLM-••••0938

## Demo roles

Create:
- Admin
- Data Engineer
- Claims Analyst
- Manager
- Auditor
- Read Only

Role behavior:
Admin sees all compliance settings and role controls.
Data Engineer sees data quality checks and pipeline status.
Claims Analyst sees claims analytics with masked identifiers.
Manager sees aggregate KPIs only.
Auditor sees audit logs and compliance dashboard.
Read Only sees summary dashboards only.

Create a RoleSwitcher component for demo purposes.

## Audit logging

Track:
- CLAIM_DETAIL_VIEWED
- MEMBER_DETAIL_VIEWED
- REPORT_EXPORTED
- ROLE_CHANGED
- ACCESS_DENIED
- DATA_QUALITY_CHECK_RUN
- DATA_QUALITY_CHECK_FAILED
- RETENTION_JOB_RAN

## App routes

Backend API should support:
- /api/dashboard/summary/
- /api/claims/
- /api/claims/<id>/
- /api/providers/performance/
- /api/payers/performance/
- /api/members/utilization/
- /api/data-quality/results/
- /api/data-quality/run/
- /api/compliance/summary/
- /api/audit-log/
- /api/exports/
- /api/about/project/

Frontend routes should support:
- /
- /claims
- /providers
- /payers
- /members
- /data-quality
- /compliance
- /audit-log
- /exports
- /about

## UI direction

Build a clean healthcare analytics command center.

Visual style:
- professional dark mode
- healthcare data operations feel
- clear KPI cards
- strong tables
- clean filters
- risk badges
- compliance status indicators
- muted gradients
- accessible contrast
- responsive mobile-first design

Avoid a generic UI.

## Environment

Create .env.example.

Use:

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/healthcare_claims_warehouse
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
VITE_API_BASE_URL=http://localhost:8000/api

Never create or commit real .env files.

## Git behavior

Set up Git after the first successful scaffold build.

Repo name:
healthcare-claims-warehouse

Do not overwrite this CLAUDE.md file.
Do not overwrite .claude/settings.json.

## README requirements

Create a professional portfolio-ready README.

Include:
- Project title
- Portfolio angle
- Problem statement
- Synthetic data notice
- HIPAA-aware disclaimer
- Tech stack
- Architecture overview
- Django backend overview
- React frontend overview
- Database layer explanation
- SQL marts list
- Data quality checks
- Role-based access explanation
- Masking strategy
- Audit logging strategy
- Export control strategy
- How to run locally
- Screenshots placeholder
- Future roadmap
- Resume bullet examples

Use this exact README wording:

This project uses synthetic healthcare claims data only. It is designed to demonstrate HIPAA-aware engineering patterns such as role-based access, minimum necessary views, masked identifiers, audit logging, export controls, retention settings, and de-identification-oriented reporting. It is not presented as a certified HIPAA-compliant production system. A production deployment handling real ePHI would require legal review, risk analysis, Business Associate Agreements, secure hosting, operational safeguards, policies, monitoring, and staff procedures.

Resume bullet:

Built a HIPAA-aware healthcare claims analytics warehouse using Python, Django, React, PostgreSQL, advanced SQL, synthetic claims data, role-based views, masked identifiers, audit logging, export controls, and data quality checks across claims, payments, denials, providers, payers, and members.

## Final QA

Review the project as:
- Senior Data Engineer
- Django Backend Engineer
- React Frontend Engineer
- Healthcare Engineering Manager
- Security-minded Reviewer
- Recruiter
- Accessibility Reviewer

Check:
- Django API quality
- React UI quality
- SQL quality
- data model quality
- dashboard clarity
- HIPAA-aware controls
- README strength
- local setup
- synthetic data safety
- no exposed secrets
- broken imports
- build errors
- mobile layout
- accessibility

Fix issues.

## Final response

Summarize:
- What was created
- How to run the backend
- How to run the frontend
- How the warehouse is structured
- What SQL marts exist
- How HIPAA-aware controls work
- Where masking logic lives
- Where audit logging lives
- What to demo first
- What should be improved next
