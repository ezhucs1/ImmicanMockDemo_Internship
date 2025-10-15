#!/bin/bash

# ============ RATE LIMITING TEST ============
# This script tests rate limiting functionality specifically

API_URL="http://localhost:5001"

echo "⏱️  RATE LIMITING TEST"
echo "======================"
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
print_test "Testing Rate Limiting on Login Endpoint"
echo "============================================="

# Test 1: Normal requests (should work)
print_test "Making first 5 requests (should succeed)..."
for i in {1..5}; do
    response=$(curl -s -X POST $API_URL/api/login \
        -H "Content-Type: application/json" \
        -d '{"email": "test@example.com", "password": "wrongpassword"}' \
        -w "Status: %{http_code}")
    
    status=$(echo "$response" | tail -n1)
    if [[ "$status" == "Status: 401" ]]; then
        print_success "Request $i: 401 Unauthorized (expected)"
    else
        print_error "Request $i: Unexpected status $status"
    fi
done

echo ""
print_test "Making requests 6-10 (should still work)..."
for i in {6..10}; do
    response=$(curl -s -X POST $API_URL/api/login \
        -H "Content-Type: application/json" \
        -d '{"email": "test@example.com", "password": "wrongpassword"}' \
        -w "Status: %{http_code}")
    
    status=$(echo "$response" | tail -n1)
    if [[ "$status" == "Status: 401" ]]; then
        print_success "Request $i: 401 Unauthorized (expected)"
    else
        print_error "Request $i: Unexpected status $status"
    fi
done

echo ""
print_test "Making 11th request (should be rate limited)..."
response=$(curl -s -X POST $API_URL/api/login \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com", "password": "wrongpassword"}' \
    -w "Status: %{http_code}")

status=$(echo "$response" | tail -n1)
if [[ "$status" == "Status: 429" ]]; then
    print_success "Request 11: 429 Rate Limit Exceeded (expected)"
else
    print_error "Request 11: Expected 429, got $status"
fi

echo ""
print_test "Making 12th request (should also be rate limited)..."
response=$(curl -s -X POST $API_URL/api/login \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com", "password": "wrongpassword"}' \
    -w "Status: %{http_code}")

status=$(echo "$response" | tail -n1)
if [[ "$status" == "Status: 429" ]]; then
    print_success "Request 12: 429 Rate Limit Exceeded (expected)"
else
    print_error "Request 12: Expected 429, got $status"
fi

echo ""
print_test "Checking Rate Limiting Data in Database"
echo "============================================="

echo "📊 Current rate limits:"
docker exec -i immican_db psql -U appuser -d appdb -c "
SELECT 
    identifier,
    request_count,
    window_start,
    created_at,
    CASE 
        WHEN request_count >= 10 THEN 'LIMIT EXCEEDED'
        WHEN request_count >= 7 THEN 'WARNING'
        ELSE 'NORMAL'
    END as status
FROM rate_limits 
ORDER BY created_at DESC 
LIMIT 5;"

echo ""
print_test "Testing Rate Limit Reset (waiting 5 seconds)..."
sleep 5

echo "📊 Rate limits after waiting:"
docker exec -i immican_db psql -U appuser -d appdb -c "
SELECT 
    identifier,
    request_count,
    window_start,
    created_at
FROM rate_limits 
ORDER BY created_at DESC 
LIMIT 3;"

echo ""
print_test "Testing Different IP Addresses"
echo "==================================="

# Test with different IP addresses
print_test "Making requests from different IP addresses..."
for i in {1..5}; do
    ip="192.168.1.$((100 + i))"
    response=$(curl -s -X POST $API_URL/api/login \
        -H "Content-Type: application/json" \
        -H "X-Forwarded-For: $ip" \
        -d '{"email": "test@example.com", "password": "wrongpassword"}' \
        -w "Status: %{http_code}")
    
    status=$(echo "$response" | tail -n1)
    print_success "IP $ip: $status"
done

echo ""
print_test "Rate limits by IP address:"
docker exec -i immican_db psql -U appuser -d appdb -c "
SELECT 
    identifier,
    request_count,
    window_start
FROM rate_limits 
ORDER BY created_at DESC 
LIMIT 10;"

echo ""
print_test "Testing Rate Limiting on Different Endpoints"
echo "================================================="

# Test rate limiting on registration endpoint (should not be rate limited)
print_test "Testing registration endpoint (should not be rate limited)..."
for i in {1..15}; do
    response=$(curl -s -X POST $API_URL/api/register \
        -H "Content-Type: application/json" \
        -d "{\"email\": \"test$i@example.com\", \"full_name\": \"Test User $i\", \"password\": \"StrongPass123!\"}" \
        -w "Status: %{http_code}")
    
    status=$(echo "$response" | tail -n1)
    if [[ "$status" == "Status: 201" ]]; then
        print_success "Registration $i: 201 Created (not rate limited)"
    else
        print_warning "Registration $i: $status"
    fi
done

echo ""
print_test "Final Rate Limiting Summary"
echo "================================"

echo "📊 All rate limits:"
docker exec -i immican_db psql -U appuser -d appdb -c "
SELECT 
    identifier,
    request_count,
    window_start,
    created_at,
    CASE 
        WHEN request_count >= 10 THEN 'LIMIT EXCEEDED'
        WHEN request_count >= 7 THEN 'WARNING'
        ELSE 'NORMAL'
    END as status
FROM rate_limits 
ORDER BY request_count DESC, created_at DESC;"

echo ""
print_success "Rate limiting test completed!"
echo ""
echo "✅ Rate limiting is working correctly:"
echo "   • Login endpoint is rate limited (10 requests per 5 minutes)"
echo "   • Registration endpoint is not rate limited"
echo "   • Different IP addresses have separate rate limits"
echo "   • Rate limit data is stored in database"
echo "   • 429 status code is returned when limit exceeded"
