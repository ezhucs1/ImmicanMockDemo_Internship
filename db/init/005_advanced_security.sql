-- ============ ADVANCED SECURITY TABLES ============

-- Security events table for comprehensive logging
CREATE TABLE IF NOT EXISTS security_events (
  id                VARCHAR(36) PRIMARY KEY,
  event_type        VARCHAR(100) NOT NULL,
  description       TEXT NOT NULL,
  user_id           VARCHAR(36) REFERENCES users_login(id) ON DELETE SET NULL,
  ip_address        VARCHAR(45), -- IPv6 compatible
  user_agent        TEXT,
  severity          VARCHAR(20) DEFAULT 'INFO', -- 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
  request_path      VARCHAR(500),
  request_method    VARCHAR(10),
  created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Suspicious activities table for threat detection
CREATE TABLE IF NOT EXISTS suspicious_activities (
  id                VARCHAR(36) PRIMARY KEY,
  pattern           TEXT NOT NULL,
  ip_address        VARCHAR(45) NOT NULL,
  event_count       INTEGER NOT NULL,
  severity          VARCHAR(20) DEFAULT 'HIGH',
  description       TEXT,
  created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Active sessions table for session management
CREATE TABLE IF NOT EXISTS active_sessions (
  id                VARCHAR(36) PRIMARY KEY,
  user_id           VARCHAR(36) NOT NULL REFERENCES users_login(id) ON DELETE CASCADE,
  user_type         VARCHAR(50) NOT NULL,
  email             VARCHAR(255) NOT NULL,
  ip_address        VARCHAR(45),
  user_agent        TEXT,
  created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_activity     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at        TIMESTAMP NOT NULL
);

-- JWT tokens table for token management (optional - for token blacklisting)
CREATE TABLE IF NOT EXISTS jwt_tokens (
  id                VARCHAR(36) PRIMARY KEY,
  user_id           VARCHAR(36) NOT NULL REFERENCES users_login(id) ON DELETE CASCADE,
  token_type        VARCHAR(20) NOT NULL, -- 'access' or 'refresh'
  token_hash        VARCHAR(255) NOT NULL, -- Hashed token for security
  expires_at        TIMESTAMP NOT NULL,
  is_revoked        BOOLEAN DEFAULT FALSE,
  created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rate limiting table for persistent rate limiting
CREATE TABLE IF NOT EXISTS rate_limits (
  id                VARCHAR(36) PRIMARY KEY,
  identifier        VARCHAR(255) NOT NULL, -- IP address or user ID
  endpoint          VARCHAR(500),
  request_count     INTEGER DEFAULT 1,
  window_start      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  window_duration   INTEGER DEFAULT 60, -- seconds
  created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Security metrics table for historical tracking
CREATE TABLE IF NOT EXISTS security_metrics (
  id                VARCHAR(36) PRIMARY KEY,
  metric_type       VARCHAR(100) NOT NULL,
  metric_value      INTEGER NOT NULL,
  time_period       VARCHAR(20) NOT NULL, -- 'hour', 'day', 'week', 'month'
  period_start      TIMESTAMP NOT NULL,
  period_end        TIMESTAMP NOT NULL,
  metadata          JSONB, -- Additional metric data
  created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_security_events_type ON security_events(event_type);
CREATE INDEX IF NOT EXISTS idx_security_events_user_id ON security_events(user_id);
CREATE INDEX IF NOT EXISTS idx_security_events_ip ON security_events(ip_address);
CREATE INDEX IF NOT EXISTS idx_security_events_created_at ON security_events(created_at);
CREATE INDEX IF NOT EXISTS idx_security_events_severity ON security_events(severity);

CREATE INDEX IF NOT EXISTS idx_suspicious_activities_ip ON suspicious_activities(ip_address);
CREATE INDEX IF NOT EXISTS idx_suspicious_activities_created_at ON suspicious_activities(created_at);

CREATE INDEX IF NOT EXISTS idx_active_sessions_user_id ON active_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_active_sessions_expires_at ON active_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_active_sessions_created_at ON active_sessions(created_at);

CREATE INDEX IF NOT EXISTS idx_jwt_tokens_user_id ON jwt_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_jwt_tokens_expires_at ON jwt_tokens(expires_at);
CREATE INDEX IF NOT EXISTS idx_jwt_tokens_revoked ON jwt_tokens(is_revoked);

CREATE INDEX IF NOT EXISTS idx_rate_limits_identifier ON rate_limits(identifier);
CREATE INDEX IF NOT EXISTS idx_rate_limits_endpoint ON rate_limits(endpoint);
CREATE INDEX IF NOT EXISTS idx_rate_limits_window_start ON rate_limits(window_start);

CREATE INDEX IF NOT EXISTS idx_security_metrics_type ON security_metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_security_metrics_period ON security_metrics(time_period);
CREATE INDEX IF NOT EXISTS idx_security_metrics_period_start ON security_metrics(period_start);

-- Function to clean up expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM active_sessions 
    WHERE expires_at < NOW();
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up expired JWT tokens
CREATE OR REPLACE FUNCTION cleanup_expired_tokens()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM jwt_tokens 
    WHERE expires_at < NOW() OR is_revoked = TRUE;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up old rate limit records
CREATE OR REPLACE FUNCTION cleanup_old_rate_limits()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM rate_limits 
    WHERE window_start < NOW() - INTERVAL '1 hour';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up old security events (keep last 30 days)
CREATE OR REPLACE FUNCTION cleanup_old_security_events()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM security_events 
    WHERE created_at < NOW() - INTERVAL '30 days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;
