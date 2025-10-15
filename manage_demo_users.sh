#!/bin/bash

# ============ DEMO USERS MANAGEMENT SCRIPT ============
# This script manages demo users: shows existing users or creates new ones
# Usage: ./manage_demo_users.sh [--create] [--show] [--clean]

API_URL="http://localhost:5001"

echo "👥 immiCan Demo Users Management"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to verify user emails
verify_user_email() {
    local email="$1"
    print_status "Verifying email for: $email"
    
    docker exec immican_db psql -U appuser -d appdb -c "
    UPDATE users_login 
    SET email_verified = TRUE 
    WHERE email = '$email';
    " > /dev/null 2>&1
    
    # Check if the update was successful
    RESULT=$(docker exec immican_db psql -U appuser -d appdb -t -c "
    SELECT email_verified 
    FROM users_login 
    WHERE email = '$email';
    " | tr -d ' ')
    
    if [ "$RESULT" = "t" ]; then
        print_success "✅ Email verified for $email"
    else
        print_warning "⚠️  Could not verify email for $email (user might not exist)"
    fi
}

# Function to display demo user credentials
display_demo_credentials() {
    echo ""
    echo "🎯 DEMO USER CREDENTIALS:"
    echo "========================="
    echo ""
    echo "👤 CLIENT ACCOUNTS:"
    echo "   📧 client@example.com"
    echo "   🔑 Password: ClientPass123!"
    echo "   🌐 Login: http://localhost:5173/login"
    echo "   📧 Email verification required before login"
    echo ""
    echo "   📧 maria@example.com"
    echo "   🔑 Password: MariaPass123!"
    echo "   🌐 Login: http://localhost:5173/login"
    echo "   📧 Email verification required before login"
    echo ""
    echo "   📧 ahmed@example.com"
    echo "   🔑 Password: AhmedPass123!"
    echo "   🌐 Login: http://localhost:5173/login"
    echo "   📧 Email verification required before login"
    echo ""
    echo "🏢 SERVICE PROVIDER ACCOUNTS:"
    echo "   📧 provider@example.com"
    echo "   🔑 Password: ProviderPass123!"
    echo "   🌐 Login: http://localhost:5173/service-provider-login"
    echo "   🏷️  Service Type: Legal"
    echo "   📧 Email verification required before login"
    echo ""
    echo "   📧 legal@example.com"
    echo "   🔑 Password: LegalPass123!"
    echo "   🌐 Login: http://localhost:5173/service-provider-login"
    echo "   🏷️  Service Type: Legal"
    echo "   📧 Email verification required before login"
    echo ""
    echo "🚀 DEMONSTRATION WORKFLOW:"
    echo "=========================="
    echo ""
    echo "1. Login as Client (client@example.com):"
    echo "   • Browse service providers"
    echo "   • Create service requests"
    echo "   • Communicate with providers"
    echo ""
    echo "2. Login as Service Provider (provider@example.com):"
    echo "   • View incoming requests"
    echo "   • Accept requests"
    echo "   • Communicate with clients"
    echo "   • Mark services as completed"
    echo ""
    echo "3. Test Complete Workflow:"
    echo "   • Client creates request"
    echo "   • Provider accepts request"
    echo "   • Both parties communicate"
    echo "   • Provider completes service"
    echo "   • Client rates and confirms"
    echo ""
    echo "🔐 EMAIL VERIFICATION:"
    echo "====================="
    echo "All users require email verification before login."
    echo "For testing, use: ./verify_email.sh user@example.com"
    echo ""
}

# Function to create demo users
create_demo_users() {
    print_status "Creating demo users..."
    
    # Create sample client users
    echo ""
    print_status "Creating client users..."
    
    # Client 1: John Client
    CLIENT1_RESPONSE=$(curl -s -X POST $API_URL/api/register \
      -H "Content-Type: application/json" \
      -d '{"email": "client@example.com", "full_name": "John Client", "password": "ClientPass123!"}')
    
    if echo "$CLIENT1_RESPONSE" | grep -q '"ok": true'; then
        print_success "✅ Client user created: client@example.com"
        verify_user_email "client@example.com"
    else
        print_error "❌ Failed to create client user: client@example.com"
    fi
    
    # Client 2: Maria Garcia
    CLIENT2_RESPONSE=$(curl -s -X POST $API_URL/api/register \
      -H "Content-Type: application/json" \
      -d '{"email": "maria@example.com", "full_name": "Maria Garcia", "password": "MariaPass123!"}')
    
    if echo "$CLIENT2_RESPONSE" | grep -q '"ok": true'; then
        print_success "✅ Client user created: maria@example.com"
        verify_user_email "maria@example.com"
    else
        print_error "❌ Failed to create client user: maria@example.com"
    fi
    
    # Client 3: Ahmed Hassan
    CLIENT3_RESPONSE=$(curl -s -X POST $API_URL/api/register \
      -H "Content-Type: application/json" \
      -d '{"email": "ahmed@example.com", "full_name": "Ahmed Hassan", "password": "AhmedPass123!"}')
    
    if echo "$CLIENT3_RESPONSE" | grep -q '"ok": true'; then
        print_success "✅ Client user created: ahmed@example.com"
        verify_user_email "ahmed@example.com"
    else
        print_error "❌ Failed to create client user: ahmed@example.com"
    fi
    
    # Create sample service provider users
    echo ""
    print_status "Creating service provider users..."
    
    # Provider 1: Jane Provider (Legal)
    PROVIDER1_RESPONSE=$(curl -s -X POST $API_URL/api/service-providers/register \
      -H "Content-Type: application/json" \
      -d '{"email": "provider@example.com", "first_name": "Jane", "last_name": "Provider", "name": "Jane Provider Services", "password": "ProviderPass123!", "service_type": "Legal", "description": "Legal services for Canadian immigration"}')
    
    if echo "$PROVIDER1_RESPONSE" | grep -q '"ok": true'; then
        print_success "✅ Service provider created: provider@example.com"
        verify_user_email "provider@example.com"
    else
        print_error "❌ Failed to create service provider: provider@example.com"
    fi
    
    # Provider 2: David Lawyer (Legal)
    PROVIDER2_RESPONSE=$(curl -s -X POST $API_URL/api/service-providers/register \
      -H "Content-Type: application/json" \
      -d '{"email": "legal@example.com", "first_name": "David", "last_name": "Lawyer", "name": "David Legal Services", "password": "LegalPass123!", "service_type": "Legal", "description": "Immigration law specialist"}')
    
    if echo "$PROVIDER2_RESPONSE" | grep -q '"ok": true'; then
        print_success "✅ Service provider created: legal@example.com"
        verify_user_email "legal@example.com"
    else
        print_error "❌ Failed to create service provider: legal@example.com"
    fi
    
    
    echo ""
    print_status "Creating sample service requests for demonstration..."
    
    # Login as client to create service requests
    CLIENT_LOGIN=$(curl -s -X POST $API_URL/api/login \
      -H "Content-Type: application/json" \
      -d '{"email": "client@example.com", "password": "ClientPass123!", "user_type": "Immigrant"}')
    
    if echo "$CLIENT_LOGIN" | grep -q '"ok": true'; then
        CLIENT_TOKEN=$(echo "$CLIENT_LOGIN" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
        CLIENT_ID=$(echo "$CLIENT_LOGIN" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
        
        print_success "✅ Client logged in successfully"
        
        # Create sample service requests
        # Request 1: Legal consultation
        REQUEST1_RESPONSE=$(curl -s -X POST $API_URL/api/service-requests \
          -H "Content-Type: application/json" \
          -H "Authorization: Bearer $CLIENT_TOKEN" \
          -d '{"service_type": "Legal", "title": "PR Application Consultation", "description": "Need help with Permanent Residence application process", "priority": "High"}')
        
        if echo "$REQUEST1_RESPONSE" | grep -q '"ok": true'; then
            print_success "✅ Service request created: PR Application Consultation"
        else
            print_warning "⚠️  Could not create service request (may require provider to exist)"
        fi
        
        # Request 2: Financial planning
        REQUEST2_RESPONSE=$(curl -s -X POST $API_URL/api/service-requests \
          -H "Content-Type: application/json" \
          -H "Authorization: Bearer $CLIENT_TOKEN" \
          -d '{"service_type": "Financial", "title": "Financial Planning for Newcomers", "description": "Need financial planning advice for settling in Canada", "priority": "Medium"}')
        
        if echo "$REQUEST2_RESPONSE" | grep -q '"ok": true'; then
            print_success "✅ Service request created: Financial Planning for Newcomers"
        else
            print_warning "⚠️  Could not create service request (may require provider to exist)"
        fi
        
    else
        print_warning "⚠️  Could not login as client to create service requests"
    fi
}

# Parse command line arguments
FORCE_CREATE=false
FORCE_SHOW=false
FORCE_CLEAN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --create)
            FORCE_CREATE=true
            shift
            ;;
        --show)
            FORCE_SHOW=true
            shift
            ;;
        --clean)
            FORCE_CLEAN=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Usage: $0 [--create] [--show] [--clean]"
            echo "  --create: Force create new demo users"
            echo "  --show: Only show existing users"
            echo "  --clean: Clean database and create fresh users"
            exit 1
            ;;
    esac
done

# Check if database is accessible
print_status "Checking database connection..."
if docker exec -i immican_db psql -U appuser -d appdb -c "SELECT 1;" > /dev/null 2>&1; then
    print_success "Database connection verified"
else
    print_error "Database not accessible. Please start the database first."
    exit 1
fi

# Check if backend is running (needed for user creation)
if [ "$FORCE_CREATE" = true ] || [ "$FORCE_CLEAN" = true ]; then
    print_status "Checking if backend server is running..."
    if curl -s http://localhost:5001/api/health > /dev/null 2>&1; then
        print_success "Backend server is running"
    else
        print_error "Backend server is not running. Please start it first:"
        echo "   cd backend && source ../venv/bin/activate && python app.py"
        exit 1
    fi
fi

# Get existing users
print_status "Checking existing users..."
EXISTING_USERS=$(docker exec -i immican_db psql -U appuser -d appdb -t -c "SELECT COUNT(*) FROM users_login;" | tr -d ' ')

if [ "$EXISTING_USERS" -gt 0 ]; then
    print_success "Found $EXISTING_USERS existing users in database"
    echo ""
    echo "📊 EXISTING USERS:"
    echo "=================="
    docker exec -i immican_db psql -U appuser -d appdb -c "SELECT email, user_type, email_verified FROM users_login ORDER BY created_date DESC;"
    echo ""
    
    if [ "$FORCE_SHOW" = true ]; then
        display_demo_credentials
        print_success "Demo users are ready for web functionality testing! 🎉"
        exit 0
    elif [ "$FORCE_CREATE" = true ] || [ "$FORCE_CLEAN" = true ]; then
        if [ "$FORCE_CLEAN" = true ]; then
            print_status "Cleaning database for fresh demo users..."
            docker exec -i immican_db psql -U appuser -d appdb < cleanup_database.sql > /dev/null 2>&1
            create_demo_users
        else
            read -p "Do you want to create additional demo users? (y/n): " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                create_demo_users
            else
                display_demo_credentials
                print_success "Demo users are ready for testing! 🎉"
                exit 0
            fi
        fi
    else
        read -p "Do you want to clean database and create fresh demo users? (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Cleaning database for fresh demo users..."
            docker exec -i immican_db psql -U appuser -d appdb < cleanup_database.sql > /dev/null 2>&1
            create_demo_users
        else
            display_demo_credentials
            print_success "Demo users are ready for testing! 🎉"
            exit 0
        fi
    fi
else
    print_status "No existing users found. Creating demo users..."
    create_demo_users
fi

echo ""
print_status "Demo users management completed!"
display_demo_credentials
print_success "Demo users are ready for web functionality testing! 🎉"
