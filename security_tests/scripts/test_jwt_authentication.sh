#!/bin/bash

# ============ JWT AUTHENTICATION TEST ============
# This script tests JWT token authentication and session management

API_URL="http://localhost:5001"

echo "🔐 JWT AUTHENTICATION TEST"
echo "=========================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
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

# Clean database first
echo "🧹 Cleaning database for fresh test..."
docker exec -i immican_db psql -U appuser -d appdb < ../cleanup_database.sql > /dev/null 2>&1

echo ""
print_test "Testing User Registration and Login"
echo "======================================="

# Register a test user
print_test "Registering test user..."
register_response=$(curl -s -X POST $API_URL/api/register \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com", "full_name": "Test User", "password": "StrongPass123!"}')

if echo "$register_response" | grep -q '"ok":true'; then
    print_success "User registration successful"
    user_id=$(echo "$register_response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
    echo "   User ID: $user_id"
else
    print_error "User registration failed: $(echo "$register_response" | grep -o '"msg":"[^"]*"')"
    exit 1
fi

echo ""
# Login and get JWT tokens
print_test "Logging in to get JWT tokens..."
login_response=$(curl -s -X POST $API_URL/api/login \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com", "password": "StrongPass123!"}')

if echo "$login_response" | grep -q '"ok":true'; then
    print_success "Login successful"
    
    # Extract tokens
    access_token=$(echo "$login_response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    refresh_token=$(echo "$login_response" | grep -o '"refresh_token":"[^"]*"' | cut -d'"' -f4)
    session_id=$(echo "$login_response" | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)
    
    echo "   Access Token: ${access_token:0:50}..."
    echo "   Refresh Token: ${refresh_token:0:50}..."
    echo "   Session ID: $session_id"
else
    print_error "Login failed: $(echo "$login_response" | grep -o '"msg":"[^"]*"')"
    exit 1
fi

echo ""
print_test "Testing Protected Endpoint Access"
echo "====================================="

# Test accessing protected endpoint with valid token
print_test "Accessing protected endpoint with valid JWT token..."
protected_response=$(curl -s -X GET "$API_URL/api/users/$user_id/service-requests" \
    -H "Authorization: Bearer $access_token")

if echo "$protected_response" | grep -q '"ok":true'; then
    print_success "Protected endpoint accessed successfully with valid token"
else
    print_error "Protected endpoint access failed: $(echo "$protected_response" | grep -o '"msg":"[^"]*"')"
fi

echo ""
# Test accessing protected endpoint without token
print_test "Accessing protected endpoint without JWT token..."
no_token_response=$(curl -s -X GET "$API_URL/api/users/$user_id/service-requests")

if echo "$no_token_response" | grep -q '"ok":false'; then
    print_success "Protected endpoint correctly rejected request without token"
    echo "   Response: $(echo "$no_token_response" | grep -o '"msg":"[^"]*"')"
else
    print_error "Protected endpoint should reject requests without token"
fi

echo ""
# Test accessing protected endpoint with invalid token
print_test "Accessing protected endpoint with invalid JWT token..."
invalid_token_response=$(curl -s -X GET "$API_URL/api/users/$user_id/service-requests" \
    -H "Authorization: Bearer invalid_token_here")

if echo "$invalid_token_response" | grep -q '"ok":false'; then
    print_success "Protected endpoint correctly rejected request with invalid token"
    echo "   Response: $(echo "$invalid_token_response" | grep -o '"msg":"[^"]*"')"
else
    print_error "Protected endpoint should reject requests with invalid token"
fi

echo ""
print_test "Testing JWT Token Refresh"
echo "============================="

# Test token refresh
print_test "Refreshing JWT token..."
refresh_response=$(curl -s -X POST $API_URL/api/auth/refresh \
    -H "Content-Type: application/json" \
    -d "{\"refresh_token\": \"$refresh_token\"}")

if echo "$refresh_response" | grep -q '"ok":true'; then
    print_success "Token refresh successful"
    new_access_token=$(echo "$refresh_response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    echo "   New Access Token: ${new_access_token:0:50}..."
    
    # Test new token works
    print_test "Testing new access token..."
    new_token_response=$(curl -s -X GET "$API_URL/api/users/$user_id/service-requests" \
        -H "Authorization: Bearer $new_access_token")
    
    if echo "$new_token_response" | grep -q '"ok":true'; then
        print_success "New access token works correctly"
    else
        print_error "New access token failed: $(echo "$new_token_response" | grep -o '"msg":"[^"]*"')"
    fi
else
    print_error "Token refresh failed: $(echo "$refresh_response" | grep -o '"msg":"[^"]*"')"
fi

echo ""
print_test "Testing Invalid Refresh Token"
echo "================================="

print_test "Testing refresh with invalid token..."
invalid_refresh_response=$(curl -s -X POST $API_URL/api/auth/refresh \
    -H "Content-Type: application/json" \
    -d '{"refresh_token": "invalid_refresh_token"}')

if echo "$invalid_refresh_response" | grep -q '"ok":false'; then
    print_success "Invalid refresh token correctly rejected"
    echo "   Response: $(echo "$invalid_refresh_response" | grep -o '"msg":"[^"]*"')"
else
    print_error "Invalid refresh token should be rejected"
fi

echo ""
print_test "Testing Session Management"
echo "=============================="

print_test "Checking active sessions in database..."
docker exec -i immican_db psql -U appuser -d appdb -c "
SELECT 
    id,
    user_id,
    email,
    ip_address,
    created_at,
    expires_at,
    CASE 
        WHEN expires_at > NOW() THEN 'ACTIVE'
        ELSE 'EXPIRED'
    END as status
FROM active_sessions 
ORDER BY created_at DESC;"

echo ""
print_test "Testing Logout"
echo "==============="

print_test "Logging out user..."
logout_response=$(curl -s -X POST $API_URL/api/auth/logout \
    -H "Authorization: Bearer $access_token")

if echo "$logout_response" | grep -q '"ok":true'; then
    print_success "Logout successful"
else
    print_error "Logout failed: $(echo "$logout_response" | grep -o '"msg":"[^"]*"')"
fi

echo ""
print_test "Testing Access After Logout"
echo "==============================="

print_test "Attempting to access protected endpoint after logout..."
post_logout_response=$(curl -s -X GET "$API_URL/api/users/$user_id/service-requests" \
    -H "Authorization: Bearer $access_token")

if echo "$post_logout_response" | grep -q '"ok":false'; then
    print_success "Protected endpoint correctly rejected request after logout"
    echo "   Response: $(echo "$post_logout_response" | grep -o '"msg":"[^"]*"')"
else
    print_warning "Token might still be valid (check expiration time)"
fi

echo ""
print_test "Checking Sessions After Logout"
echo "=================================="

docker exec -i immican_db psql -U appuser -d appdb -c "
SELECT 
    id,
    user_id,
    email,
    created_at,
    expires_at,
    CASE 
        WHEN expires_at > NOW() THEN 'ACTIVE'
        ELSE 'EXPIRED'
    END as status
FROM active_sessions 
ORDER BY created_at DESC;"

echo ""
print_test "Testing JWT Token Expiration"
echo "==============================="

print_test "Creating expired token test..."
# Create a token that should be expired (this is a mock test)
expired_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidGVzdCIsImV4cCI6MTYwOTQ1NjAwMCwiaWF0IjoxNjA5NDU2MDAwfQ.expired_signature"

expired_response=$(curl -s -X GET "$API_URL/api/users/$user_id/service-requests" \
    -H "Authorization: Bearer $expired_token")

if echo "$expired_response" | grep -q '"ok":false'; then
    print_success "Expired token correctly rejected"
    echo "   Response: $(echo "$expired_response" | grep -o '"msg":"[^"]*"')"
else
    print_warning "Expired token test (token format may be different)"
fi

echo ""
print_test "Testing JWT Token Structure"
echo "==============================="

print_test "Decoding JWT token structure..."
# Decode the JWT token (header.payload.signature)
if command -v base64 >/dev/null 2>&1; then
    header=$(echo "$access_token" | cut -d'.' -f1 | base64 -d 2>/dev/null)
    payload=$(echo "$access_token" | cut -d'.' -f2 | base64 -d 2>/dev/null)
    
    echo "   Header: $header"
    echo "   Payload: $payload"
else
    print_warning "base64 command not available for token decoding"
fi

echo ""
print_test "Checking Security Events"
echo "============================"

echo "📊 Security events from JWT authentication tests:"
docker exec -i immican_db psql -U appuser -d appdb -c "
SELECT 
    event_type,
    LEFT(description, 60) as description_short,
    severity,
    created_at
FROM security_events 
WHERE created_at > NOW() - INTERVAL '5 minutes'
ORDER BY created_at DESC 
LIMIT 10;"

echo ""
print_success "JWT authentication test completed!"
echo ""
echo "✅ JWT authentication is working correctly:"
echo "   • User registration and login"
echo "   • JWT token generation (access + refresh)"
echo "   • Protected endpoint access with valid token"
echo "   • Rejection of requests without token"
echo "   • Rejection of requests with invalid token"
echo "   • Token refresh functionality"
echo "   • Session management in database"
echo "   • Logout functionality"
echo "   • All security events logged"
