-- Mart: daily compliance/audit activity summary, aggregated from
-- audit.audit_events (populated by the audit logging service).

CREATE TABLE IF NOT EXISTS marts.mart_compliance_audit_summary (
    activity_date       date NOT NULL,
    action               text NOT NULL,
    event_count           integer NOT NULL,
    distinct_users        integer NOT NULL,
    failed_count           integer NOT NULL,
    last_event_at           timestamptz NOT NULL,
    PRIMARY KEY (activity_date, action)
);

TRUNCATE marts.mart_compliance_audit_summary;

INSERT INTO marts.mart_compliance_audit_summary (
    activity_date, action, event_count, distinct_users, failed_count, last_event_at
)
SELECT
    event_timestamp::date AS activity_date,
    action,
    count(*)                                          AS event_count,
    count(DISTINCT user_id)                            AS distinct_users,
    sum(CASE WHEN status = 'DENIED' THEN 1 ELSE 0 END)  AS failed_count,
    max(event_timestamp)                                 AS last_event_at
FROM audit.audit_events
GROUP BY 1, 2
ORDER BY activity_date DESC, event_count DESC;
