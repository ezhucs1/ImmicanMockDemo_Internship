#!/bin/bash

# ============ immiCan Setup Script ============
# This script sets up the entire immiCan application from scratch

set -e  # Exit on any error

echo "🏠 Setting up immiCan - Canadian Immigration Services Platform"
echo "=============================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.12+ first."
    exit 1
fi

print_status "All prerequisites are installed ✅"

# Step 1: Setup Database
print_status "Setting up PostgreSQL database..."
if docker ps -a | grep -q immican_db; then
    print_warning "Database container already exists. Removing..."
    docker stop immican_db 2>/dev/null || true
    docker rm immican_db 2>/dev/null || true
fi

docker run -d \
  --name immican_db \
  -e POSTGRES_DB=appdb \
  -e POSTGRES_USER=appuser \
  -e POSTGRES_PASSWORD=apppass \
  -p 5432:5432 \
  postgres:16

print_success "Database container started"

# Wait for database to be ready
print_status "Waiting for database to be ready..."
sleep 5

# Initialize database schema
print_status "Initializing database schema..."
docker exec -i immican_db psql -U appuser -d appdb < db/init/000_core.sql
docker exec -i immican_db psql -U appuser -d appdb < db/init/002_service_providers.sql
docker exec -i immican_db psql -U appuser -d appdb < db/init/003_messaging.sql
docker exec -i immican_db psql -U appuser -d appdb < db/init/004_rating_system.sql
docker exec -i immican_db psql -U appuser -d appdb < db/init/005_advanced_security.sql
docker exec -i immican_db psql -U appuser -d appdb < db/init/006_email_verification.sql

print_success "Database schema initialized"

# Step 1.5: Setup Database Admin Tools
print_status "Setting up database admin tools..."

# Get the Docker network name (it might be different)
NETWORK_NAME=$(docker inspect immican_db --format='{{range .NetworkSettings.Networks}}{{.NetworkID}}{{end}}' | xargs docker network inspect --format='{{.Name}}' 2>/dev/null || echo "bridge")

# Setup Adminer
if docker ps -a | grep -q immican_adminer; then
    print_warning "Adminer container already exists. Removing..."
    docker stop immican_adminer 2>/dev/null || true
    docker rm immican_adminer 2>/dev/null || true
fi

docker run -d \
  --name immican_adminer \
  --network "$NETWORK_NAME" \
  -p 8080:8080 \
  adminer:latest

print_success "Adminer setup completed (http://localhost:8080)"

# Setup pgAdmin
if docker ps -a | grep -q immican_pgadmin; then
    print_warning "pgAdmin container already exists. Removing..."
    docker stop immican_pgadmin 2>/dev/null || true
    docker rm immican_pgadmin 2>/dev/null || true
fi

docker run -d \
  --name immican_pgadmin \
  -e PGADMIN_DEFAULT_EMAIL=admin@admin.com \
  -e PGADMIN_DEFAULT_PASSWORD=admin \
  -p 5050:80 \
  dpage/pgadmin4:latest

print_success "pgAdmin setup completed (http://localhost:5050)"

# Step 2: Setup Backend
print_status "Setting up Python backend..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install flask flask-cors flask-socketio sqlalchemy psycopg2-binary python-dotenv PyJWT

# Create .env file
print_status "Creating environment configuration..."
echo "DATABASE_URL=postgresql+psycopg2://appuser:apppass@localhost:5432/appdb" > .env

print_success "Backend setup completed"

# Step 3: Setup Frontend
print_status "Setting up React frontend..."
cd frontend-react

# Install Node.js dependencies
if [ ! -d "node_modules" ]; then
    print_status "Installing Node.js dependencies..."
    npm install
fi

print_success "Frontend setup completed"
cd ..

# Step 4: Verify setup
print_status "Verifying setup..."

# Check database connection
if docker exec immican_db psql -U appuser -d appdb -c "SELECT 1;" > /dev/null 2>&1; then
    print_success "Database connection verified"
else
    print_error "Database connection failed"
    exit 1
fi

# Check if tables exist
TABLE_COUNT=$(docker exec immican_db psql -U appuser -d appdb -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | tr -d ' ')
if [ "$TABLE_COUNT" -gt 10 ]; then
    print_success "Database tables created ($TABLE_COUNT tables)"
else
    print_error "Database tables not created properly"
    exit 1
fi

print_success "Setup verification completed"

# Step 5: Create Sample Users for Demonstration
print_status "Creating sample users for demonstration..."

# Wait for backend to be ready (if running)
sleep 2

# Use the manage_demo_users.sh script to create users
if [ -f "manage_demo_users.sh" ]; then
    print_status "Using manage_demo_users.sh to create demo users..."
    chmod +x manage_demo_users.sh
    ./manage_demo_users.sh --create
    print_success "Demo users created using manage_demo_users.sh"
else
    print_warning "manage_demo_users.sh not found. Skipping demo user creation."
    print_status "You can create demo users later using: ./manage_demo_users.sh --create"
fi

# Step 6: Display next steps
echo ""
echo "🎉 Setup completed successfully!"
echo "================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Start the backend server:"
echo "   cd backend && source ../venv/bin/activate && python app.py"
echo ""
echo "2. Start the frontend server (in a new terminal):"
echo "   cd frontend-react && npm run dev"
echo ""
echo "3. Access the application:"
echo "   Frontend: http://localhost:5173 (or 5175 if 5173 is in use)"
echo "   Backend API: http://localhost:5001"
echo "   Database Admin (Adminer): http://localhost:8080"
echo "     - System: PostgreSQL"
echo "     - Server: immican_db"
echo "     - Username: appuser, Password: apppass, Database: appdb"
echo "   Database Admin (pgAdmin): http://localhost:5050"
echo "     - Login: admin@admin.com / admin"
echo "     - Add Server: localhost:5432, appuser/apppass, appdb"
echo ""
echo "4. Demo Users Management:"
echo "   📋 Show existing users: ./manage_demo_users.sh --show"
echo "   🔄 Create new users: ./manage_demo_users.sh --create"
echo "   🧹 Clean and recreate: ./manage_demo_users.sh --clean"
echo ""
echo "   👤 Sample Client Accounts:"
echo "      Email: client@example.com, maria@example.com, ahmed@example.com"
echo "      Password: ClientPass123!, MariaPass123!, AhmedPass123!"
echo "      Login: http://localhost:5173/login"
echo ""
echo "   🏢 Sample Service Provider Accounts:"
echo "      Email: provider@example.com, legal@example.com"
echo "      Password: ProviderPass123!, LegalPass123!"
echo "      Login: http://localhost:5173/service-provider-login"
echo ""
echo "5. Email verification (for testing):"
echo "   ./verify_email.sh user@example.com"
echo ""
echo "6. Monitor security events:"
echo "   docker exec -i immican_db psql -U appuser -d appdb -c \"SELECT * FROM security_events ORDER BY created_at DESC LIMIT 10;\""
echo ""
echo "7. Clean database for fresh testing:"
echo "   docker exec -i immican_db psql -U appuser -d appdb < cleanup_database.sql"
echo ""
print_success "immiCan is ready for development and testing! 🚀"
