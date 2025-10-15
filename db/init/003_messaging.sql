-- ============ MESSAGING TABLES ============

CREATE TABLE IF NOT EXISTS conversations (
  id                VARCHAR(36) PRIMARY KEY,
  service_request_id VARCHAR(36) NOT NULL REFERENCES service_requests(id) ON DELETE CASCADE,
  user_id           VARCHAR(36) NOT NULL REFERENCES users_login(id) ON DELETE CASCADE,
  provider_id       VARCHAR(36) NOT NULL REFERENCES service_providers(id) ON DELETE CASCADE,
  status            VARCHAR(50) DEFAULT 'ACTIVE', -- 'ACTIVE', 'CLOSED'
  created_date      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_date      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(service_request_id) -- One conversation per service request
);

CREATE TABLE IF NOT EXISTS messages (
  id                VARCHAR(36) PRIMARY KEY,
  conversation_id   VARCHAR(36) NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  sender_id         VARCHAR(36) NOT NULL, -- Can be user_id or provider_id
  sender_type       VARCHAR(20) NOT NULL, -- 'CLIENT' or 'PROVIDER'
  message_text      TEXT NOT NULL,
  is_read           BOOLEAN DEFAULT FALSE,
  created_date      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============ INDEXES ============
CREATE INDEX IF NOT EXISTS idx_conversations_service_request ON conversations(service_request_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_provider_id ON conversations(provider_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_sender_id ON messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_date ON messages(created_date);

-- ============ TRIGGERS ============
-- Update conversation timestamp when new message is added
CREATE OR REPLACE FUNCTION trg_update_conversation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE conversations 
  SET updated_date = NOW() 
  WHERE id = NEW.conversation_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_messages_update_conversation
  AFTER INSERT ON messages
  FOR EACH ROW
  EXECUTE FUNCTION trg_update_conversation_timestamp();
