-- ============ SERVICE PROVIDER TABLES ============

CREATE TABLE IF NOT EXISTS service_providers (
  id                VARCHAR(36) PRIMARY KEY,
  name              VARCHAR(255) NOT NULL,
  email             VARCHAR(255) UNIQUE NOT NULL,
  phone             VARCHAR(255),
  address           VARCHAR(500),
  service_type      VARCHAR(100) NOT NULL, -- 'Legal', 'Medical', 'Education', 'Employment', 'Housing', 'Other'
  description       TEXT,
  website           VARCHAR(255),
  is_active         BOOLEAN DEFAULT TRUE,
  rating            DECIMAL(3,2) DEFAULT 0.0,
  total_reviews     INTEGER DEFAULT 0,
  created_date      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_date      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS service_requests (
  id                VARCHAR(36) PRIMARY KEY,
  user_id           VARCHAR(36) NOT NULL REFERENCES users_login(id) ON DELETE CASCADE,
  provider_id       VARCHAR(36) NOT NULL REFERENCES service_providers(id) ON DELETE CASCADE,
  service_type      VARCHAR(100) NOT NULL,
  title             VARCHAR(255) NOT NULL,
  description       TEXT,
  status            VARCHAR(50) DEFAULT 'PENDING', -- 'PENDING', 'ACCEPTED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'
  priority          VARCHAR(20) DEFAULT 'MEDIUM', -- 'LOW', 'MEDIUM', 'HIGH', 'URGENT'
  requested_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  accepted_date     TIMESTAMP,
  completed_date    TIMESTAMP,
  notes             TEXT,
  created_date      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_date      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS service_reviews (
  id                VARCHAR(36) PRIMARY KEY,
  service_request_id VARCHAR(36) NOT NULL REFERENCES service_requests(id) ON DELETE CASCADE,
  user_id           VARCHAR(36) NOT NULL REFERENCES users_login(id) ON DELETE CASCADE,
  provider_id       VARCHAR(36) NOT NULL REFERENCES service_providers(id) ON DELETE CASCADE,
  rating            INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
  comment           TEXT,
  created_date      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============ INDEXES ============
CREATE INDEX IF NOT EXISTS idx_service_requests_user_id ON service_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_service_requests_provider_id ON service_requests(provider_id);
CREATE INDEX IF NOT EXISTS idx_service_requests_status ON service_requests(status);
CREATE INDEX IF NOT EXISTS idx_service_providers_service_type ON service_providers(service_type);
CREATE INDEX IF NOT EXISTS idx_service_providers_active ON service_providers(is_active);

-- ============ SAMPLE SERVICE PROVIDERS ============
INSERT INTO service_providers (id, name, email, phone, address, service_type, description, website) VALUES
('sp-001', 'Canadian Immigration Law Firm', 'info@canadianimmigrationlaw.com', '+1-416-555-0101', '123 Bay Street, Toronto, ON M5H 2Y4', 'Legal', 'Expert immigration lawyers specializing in Canadian immigration processes, work permits, and permanent residency applications.', 'https://canadianimmigrationlaw.com'),
('sp-002', 'Newcomer Health Clinic', 'health@newcomerclinic.ca', '+1-416-555-0102', '456 Queen Street West, Toronto, ON M5V 2A9', 'Medical', 'Comprehensive healthcare services for newcomers including medical exams, vaccinations, and health insurance guidance.', 'https://newcomerclinic.ca'),
('sp-003', 'Skills Training Institute', 'training@skillsinstitute.ca', '+1-416-555-0103', '789 King Street East, Toronto, ON M5C 1B6', 'Education', 'Professional development and skills training programs to help newcomers integrate into the Canadian workforce.', 'https://skillsinstitute.ca'),
('sp-004', 'Job Connect Services', 'jobs@jobconnect.ca', '+1-416-555-0104', '321 Yonge Street, Toronto, ON M5B 1R3', 'Employment', 'Employment services including resume writing, job search assistance, and interview preparation for newcomers.', 'https://jobconnect.ca'),
('sp-005', 'Housing Solutions Inc.', 'housing@housingsolutions.ca', '+1-416-555-0105', '654 College Street, Toronto, ON M6G 1B4', 'Housing', 'Rental assistance and housing support services for newcomers, including temporary accommodation and rental applications.', 'https://housingsolutions.ca')
ON CONFLICT (id) DO NOTHING;
