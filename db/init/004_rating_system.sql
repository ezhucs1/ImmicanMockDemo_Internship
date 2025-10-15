-- Add rating and confirmation fields to service_requests table
ALTER TABLE service_requests 
ADD COLUMN IF NOT EXISTS client_rating INTEGER CHECK (client_rating >= 1 AND client_rating <= 5),
ADD COLUMN IF NOT EXISTS confirmed_date TIMESTAMP;

-- Update status enum to include CONFIRMED
-- Note: PostgreSQL doesn't have easy enum modification, so we'll handle this in the application
-- The status field will accept 'CONFIRMED' as a string value

-- Add index for better performance on rating queries
CREATE INDEX IF NOT EXISTS idx_service_requests_client_rating ON service_requests(client_rating) WHERE client_rating IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_service_requests_confirmed_date ON service_requests(confirmed_date) WHERE confirmed_date IS NOT NULL;
