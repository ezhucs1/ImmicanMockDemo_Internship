# 🚀 Quick Commands Reference

## **Setup & Installation**

```bash
# Complete setup (first time only)
./setup.sh

# Create demo users for testing (after backend is running)
./create_demo_users.sh

# Verify user emails manually (for testing)
./verify_email.sh user@example.com

# Manual setup steps
docker run -d --name immican_db -e POSTGRES_DB=appdb -e POSTGRES_USER=appuser -e POSTGRES_PASSWORD=apppass -p 5432:5432 postgres:16
docker exec -i immican_db psql -U appuser -d appdb < db/init/000_core.sql
docker exec -i immican_db psql -U appuser -d appdb < db/init/002_service_providers.sql
docker exec -i immican_db psql -U appuser -d appdb < db/init/003_messaging.sql
docker exec -i immican_db psql -U appuser -d appdb < db/init/004_rating_system.sql
docker exec -i immican_db psql -U appuser -d appdb < db/init/005_advanced_security.sql
docker exec -i immican_db psql -U appuser -d appdb < db/init/006_email_verification.sql
```

## **Development Servers**

```bash
# Start backend (Terminal 1)
cd backend && source ../venv/bin/activate && python app.py

# Start frontend (Terminal 2)
cd frontend-react && npm run dev
```

## **Demo Users for Testing**

### **Pre-created Demo Accounts**
```bash
# Manage demo users (show existing or create new)
./manage_demo_users.sh

# Show only existing users
./manage_demo_users.sh --show

# Force create new demo users
./manage_demo_users.sh --create

# Clean database and create fresh users
./manage_demo_users.sh --clean
```

### **Demo User Credentials**
```bash
# CLIENT ACCOUNTS:
# Email: client@example.com
# Password: ClientPass123!
# Login: http://localhost:5173/login

# Email: maria@example.com  
# Password: MariaPass123!
# Login: http://localhost:5173/login

# SERVICE PROVIDER ACCOUNTS:
# Email: provider@example.com
# Password: ProviderPass123!
# Login: http://localhost:5173/service-provider-login

# Email: legal@example.com
# Password: LegalPass123!
# Login: http://localhost:5173/service-provider-login
```

## **Web Functionality Testing**

### **API Health Check**
```bash
# Test backend health
curl http://localhost:5001/api/health
```

### **User Registration Testing**
```bash
# Test client registration
curl -X POST http://localhost:5001/api/register \
  -H "Content-Type: application/json" \
  -d '{"email": "client@example.com", "full_name": "John Client", "password": "StrongPass123!"}'

# Test service provider registration
curl -X POST http://localhost:5001/api/service-providers/register \
  -H "Content-Type: application/json" \
  -d '{"email": "provider@example.com", "first_name": "Jane", "last_name": "Provider", "name": "Jane Provider Services", "password": "StrongPass123!", "service_type": "Legal", "description": "Legal services for immigrants"}'
```

### **Authentication Testing**
```bash
# Test client login (with user_type validation)
curl -X POST http://localhost:5001/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "client@example.com", "password": "StrongPass123!", "user_type": "Immigrant"}'

# Test service provider login (with user_type validation)
curl -X POST http://localhost:5001/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "provider@example.com", "password": "StrongPass123!", "user_type": "ServiceProvider"}'

# Test cross-login security (should fail)
curl -X POST http://localhost:5001/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "provider@example.com", "password": "StrongPass123!", "user_type": "Immigrant"}'
```

### **Service Request Testing**
```bash
# Create service request (requires JWT token)
curl -X POST http://localhost:5001/api/service-requests \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"service_type": "Legal", "title": "Immigration Consultation", "description": "Need help with PR application", "priority": "High"}'

# Get user's service requests
curl -X GET http://localhost:5001/api/users/USER_ID/service-requests \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### **Messaging System Testing**
```bash
# Get conversations
curl -X GET http://localhost:5001/api/users/USER_ID/conversations \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Send message
curl -X POST http://localhost:5001/api/conversations/CONVERSATION_ID/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"content": "Hello, I need help with my application"}'
```

## **Email Verification System**

```bash
# Manual email verification (for testing)
./verify_email.sh user@example.com

# Verify email with token (API)
curl -X POST http://localhost:5001/api/verify-email \
  -H "Content-Type: application/json" \
  -d '{"token": "your_verification_token"}'

# Resend verification email
curl -X POST http://localhost:5001/api/resend-verification \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# View verification tokens
docker exec -i immican_db psql -U appuser -d appdb -c "SELECT * FROM email_verification_tokens LIMIT 5;"
```

## **Database Administration**

### **Web-Based Admin Tools**
```bash
# Adminer (Recommended)
# URL: http://localhost:8080
# Server: immican_db, User: appuser, Password: apppass, Database: appdb

# pgAdmin (Professional)
# URL: http://localhost:5050
# Login: admin@admin.com / admin
# Add Server: localhost:5432, appuser/apppass, appdb
```

### **Command Line Database Management**
```bash
# View all tables
docker exec -i immican_db psql -U appuser -d appdb -c "\dt"

# Check table structure
docker exec -i immican_db psql -U appuser -d appdb -c "\d users_login"

# View user data
docker exec -i immican_db psql -U appuser -d appdb -c "SELECT * FROM users_login LIMIT 5;"

# View service requests
docker exec -i immican_db psql -U appuser -d appdb -c "SELECT * FROM service_requests LIMIT 5;"

# View conversations
docker exec -i immican_db psql -U appuser -d appdb -c "SELECT * FROM conversations LIMIT 5;"

# View messages
docker exec -i immican_db psql -U appuser -d appdb -c "SELECT * FROM messages LIMIT 5;"

# View security events
docker exec -i immican_db psql -U appuser -d appdb -c "SELECT * FROM security_events ORDER BY created_at DESC LIMIT 10;"

# Clean all data
docker exec -i immican_db psql -U appuser -d appdb < cleanup_database.sql
```

## **Frontend Testing**

### **Development Server**
```bash
# Start frontend development server
cd frontend-react
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### **Frontend URLs**
- **Development**: http://localhost:5173
- **Client Registration**: http://localhost:5173/register
- **Service Provider Registration**: http://localhost:5173/service-provider-register
- **Client Login**: http://localhost:5173/login
- **Service Provider Login**: http://localhost:5173/service-provider-login
- **Client Dashboard**: http://localhost:5173/dashboard
- **Service Provider Dashboard**: http://localhost:5173/service-provider-dashboard

## **Backend Testing**

### **API Endpoints**
```bash
# Health check
curl http://localhost:5001/api/health

# User registration
curl -X POST http://localhost:5001/api/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "full_name": "Test User", "password": "StrongPass123!"}'

# User login
curl -X POST http://localhost:5001/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "StrongPass123!"}'

# Service provider registration
curl -X POST http://localhost:5001/api/service-providers/register \
  -H "Content-Type: application/json" \
  -d '{"email": "provider@example.com", "first_name": "John", "last_name": "Doe", "name": "Test Services", "password": "StrongPass123!", "service_type": "Legal", "description": "Test description"}'

# Get service requests (requires JWT)
curl -X GET http://localhost:5001/api/users/USER_ID/service-requests \
  -H "Authorization: Bearer JWT_TOKEN"
```

## **Real-Time Messaging Testing**

### **WebSocket Connection**
```bash
# Test WebSocket connection (requires socket.io client)
# Connect to: http://localhost:5001
# Join conversation: socket.emit('join_conversation', {conversation_id: 'CONVERSATION_ID'})
# Send message: socket.emit('send_message', {conversation_id: 'CONVERSATION_ID', content: 'Hello'})
```

### **Message Flow Testing**
```bash
# 1. Create service request
# 2. Provider accepts request
# 3. Conversation is created
# 4. Both parties can send messages
# 5. Messages are stored in database
# 6. Real-time updates via WebSocket
```

## **Security Testing**

```bash
# For comprehensive security testing
# See security_tests/ folder for organized testing suite
cd security_tests
./scripts/demo_security_working.sh
```

## **Troubleshooting**

```bash
# Check if database is running
docker ps | grep immican_db

# Check database logs
docker logs immican_db

# Restart database
docker restart immican_db

# Check backend logs
cd backend && python app.py

# Check frontend build
cd frontend-react && npm run build

# Reset everything (nuclear option)
docker stop immican_db && docker rm immican_db
./setup.sh
```

## **Production Deployment**

```bash
# Build frontend for production
cd frontend-react
npm run build

# Start backend in production mode
cd backend
source ../venv/bin/activate
export FLASK_ENV=production
python app.py

# Use production database
export DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

## **Useful URLs**

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5001
- **API Health**: http://localhost:5001/api/health
- **Database**: localhost:5432

## **Key Files**

- **README.md**: Complete technical documentation
- **USER_GUIDE.md**: Comprehensive user guide for clients and service providers
- **setup.sh**: Automated setup script
- **cleanup_database.sql**: Database cleanup script
- **backend/app.py**: Main Flask application
- **frontend-react/src/**: React components
- **db/init/**: Database schema files
- **security_tests/**: Comprehensive security testing suite