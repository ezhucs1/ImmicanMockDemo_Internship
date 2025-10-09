-- ============ CORE TABLES ============

CREATE TABLE IF NOT EXISTS users_login (
  id              VARCHAR(36) PRIMARY KEY,
  email           VARCHAR(255) UNIQUE NOT NULL,
  password_hash   VARCHAR(255) NOT NULL,
  user_type       VARCHAR(50)  DEFAULT 'Immigrant',
  is_locked       BOOLEAN      DEFAULT FALSE,
  is_active       BOOLEAN      DEFAULT TRUE,
  email_verified  BOOLEAN      DEFAULT FALSE,
  login_attempts  INTEGER      DEFAULT 0,
  last_login      TIMESTAMP,
  attempt_time    TIMESTAMP,
  login_status    VARCHAR(50),
  created_date    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS immigrant_profile (
  id                   VARCHAR(36) PRIMARY KEY,
  user_id              VARCHAR(36) UNIQUE NOT NULL REFERENCES users_login(id) ON DELETE CASCADE,
  first_name           VARCHAR(255),
  last_name            VARCHAR(255),
  email                VARCHAR(255),
  phone                VARCHAR(255),
  age                  NUMERIC,
  country_residence    VARCHAR(255),
  desired_destination  VARCHAR(255),
  marital_status       VARCHAR(255),
  family_members       NUMERIC,
  referral_source      VARCHAR(255),
  about                VARCHAR(500),
  address              VARCHAR(255),
  profile_allow        BOOLEAN DEFAULT TRUE,
  created_date         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_log (
  id           BIGSERIAL PRIMARY KEY,
  action_type  VARCHAR(50) NOT NULL,     -- SIGNUP | LOGIN_SUCCESS | LOGIN_FAILURE | LOGOUT | VERIFY_EMAIL | UPDATE_PROFILE | etc.
  description  TEXT,
  created_by   VARCHAR(36),              -- user_id if known
  created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  ip_address   INET,
  user_agent   TEXT
);

-- ============ OPTIONAL LOOKUPS ============
-- (If you want your dropdowns like Desired Destination, Referral Source, etc.,
--  import your existing lookup tables and seed rows later. You can do this AFTER core is live.)

-- ============ TRIGGERS (AUTO-LOGGING) ============
CREATE OR REPLACE FUNCTION trg_log_new_user()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO audit_log(action_type, description, created_by)
  VALUES ('SIGNUP', 'User created account', NEW.id);
  RETURN NEW;
END$$;

DROP TRIGGER IF EXISTS t_users_login_after_insert ON users_login;
CREATE TRIGGER t_users_login_after_insert
AFTER INSERT ON users_login
FOR EACH ROW EXECUTE FUNCTION trg_log_new_user();

-- Example helper for login attempt updates: not auto-triggered, we’ll call from backend,
-- but keep this function if you prefer SQL-only logging hooks later.
CREATE OR REPLACE FUNCTION log_event(p_user_id VARCHAR, p_type VARCHAR, p_desc TEXT, p_ip INET, p_ua TEXT)
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO audit_log(action_type, description, created_by, ip_address, user_agent)
  VALUES (p_type, p_desc, p_user_id, p_ip, p_ua);
END$$;
