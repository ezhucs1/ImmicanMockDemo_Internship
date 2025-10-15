-- ============ DATABASE CLEANUP SCRIPT ============
-- This script will delete all data while keeping the table structure intact

-- Delete all data from all tables (in correct order due to foreign key constraints)

-- 1. Delete security-related data first
DELETE FROM email_verification_tokens;
DELETE FROM security_events;
DELETE FROM suspicious_activities;
DELETE FROM active_sessions;
DELETE FROM jwt_tokens;
DELETE FROM rate_limits;
DELETE FROM security_metrics;

-- 2. Delete messaging data
DELETE FROM messages;
DELETE FROM conversations;

-- 3. Delete service-related data
DELETE FROM service_requests;
DELETE FROM service_reviews;

-- 4. Delete user profile data
DELETE FROM immigrant_profile;
DELETE FROM service_providers;

-- 5. Delete audit logs
DELETE FROM audit_log;

-- 6. Delete user login data (this will cascade delete related data)
DELETE FROM users_login;

-- 7. Reset any sequences or auto-increment counters (if any)
-- Note: PostgreSQL doesn't use sequences for UUID primary keys, so this is not needed

-- 8. Verify cleanup
SELECT 'email_verification_tokens' as table_name, COUNT(*) as remaining_rows FROM email_verification_tokens
UNION ALL
SELECT 'security_events', COUNT(*) FROM security_events
UNION ALL
SELECT 'suspicious_activities', COUNT(*) FROM suspicious_activities
UNION ALL
SELECT 'active_sessions', COUNT(*) FROM active_sessions
UNION ALL
SELECT 'jwt_tokens', COUNT(*) FROM jwt_tokens
UNION ALL
SELECT 'rate_limits', COUNT(*) FROM rate_limits
UNION ALL
SELECT 'security_metrics', COUNT(*) FROM security_metrics
UNION ALL
SELECT 'messages', COUNT(*) FROM messages
UNION ALL
SELECT 'conversations', COUNT(*) FROM conversations
UNION ALL
SELECT 'service_requests', COUNT(*) FROM service_requests
UNION ALL
SELECT 'service_reviews', COUNT(*) FROM service_reviews
UNION ALL
SELECT 'immigrant_profile', COUNT(*) FROM immigrant_profile
UNION ALL
SELECT 'service_providers', COUNT(*) FROM service_providers
UNION ALL
SELECT 'audit_log', COUNT(*) FROM audit_log
UNION ALL
SELECT 'users_login', COUNT(*) FROM users_login
ORDER BY table_name;
