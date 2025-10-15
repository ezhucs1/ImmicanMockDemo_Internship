#!/bin/bash

# ============ MASTER SECURITY TEST RUNNER ============
# This script runs all individual security tests

echo "🛡️  COMPREHENSIVE SECURITY TEST SUITE"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=5

echo "This comprehensive test suite will run all security feature tests individually."
echo "Each test focuses on a specific security aspect to demonstrate functionality."
echo ""

read -p "Press Enter to continue or Ctrl+C to cancel..."

echo ""
print_header "TEST 1: RATE LIMITING"
echo "Testing rate limiting functionality..."
echo ""

if ./test_rate_limiting.sh; then
    print_success "Rate limiting test completed successfully"
    ((TESTS_PASSED++))
else
    print_error "Rate limiting test failed"
    ((TESTS_FAILED++))
fi

echo ""
echo "Press Enter to continue to next test..."
read

echo ""
print_header "TEST 2: INPUT VALIDATION"
echo "Testing input validation and sanitization..."
echo ""

if ./test_input_validation.sh; then
    print_success "Input validation test completed successfully"
    ((TESTS_PASSED++))
else
    print_error "Input validation test failed"
    ((TESTS_FAILED++))
fi

echo ""
echo "Press Enter to continue to next test..."
read

echo ""
print_header "TEST 3: JWT AUTHENTICATION"
echo "Testing JWT token authentication and management..."
echo ""

if ./test_jwt_authentication.sh; then
    print_success "JWT authentication test completed successfully"
    ((TESTS_PASSED++))
else
    print_error "JWT authentication test failed"
    ((TESTS_FAILED++))
fi

echo ""
echo "Press Enter to continue to next test..."
read

echo ""
print_header "TEST 4: SECURITY MONITORING"
echo "Testing security event logging and monitoring..."
echo ""

if ./test_security_monitoring.sh; then
    print_success "Security monitoring test completed successfully"
    ((TESTS_PASSED++))
else
    print_error "Security monitoring test failed"
    ((TESTS_FAILED++))
fi

echo ""
echo "Press Enter to continue to next test..."
read

echo ""
print_header "TEST 5: SESSION MANAGEMENT"
echo "Testing session management and JWT token handling..."
echo ""

if ./test_session_management.sh; then
    print_success "Session management test completed successfully"
    ((TESTS_PASSED++))
else
    print_error "Session management test failed"
    ((TESTS_FAILED++))
fi

echo ""
print_header "FINAL TEST RESULTS"
echo "==================="

echo ""
echo "📊 Test Summary:"
echo "   Total Tests: $TOTAL_TESTS"
echo "   Passed: $TESTS_PASSED"
echo "   Failed: $TESTS_FAILED"
echo "   Success Rate: $(( (TESTS_PASSED * 100) / TOTAL_TESTS ))%"

echo ""
if [ $TESTS_FAILED -eq 0 ]; then
    print_success "🎉 ALL SECURITY TESTS PASSED!"
    echo ""
    echo "✅ Security Features Verified:"
    echo "   • Rate limiting prevents brute force attacks"
    echo "   • Input validation blocks injection attacks"
    echo "   • JWT authentication secures API endpoints"
    echo "   • Security monitoring logs all activities"
    echo "   • Session management handles user sessions"
    echo ""
    echo "🛡️  Your application has enterprise-grade security!"
else
    print_error "❌ Some tests failed. Please review the output above."
    echo ""
    echo "🔍 Failed tests need attention:"
    echo "   • Check the error messages above"
    echo "   • Verify backend server is running"
    echo "   • Ensure database is accessible"
    echo "   • Review security configuration"
fi

echo ""
print_header "INDIVIDUAL TEST COMMANDS"
echo "============================"

echo ""
echo "To run individual tests:"
echo ""
echo "1. Rate Limiting:"
echo "   ./security_tests/test_rate_limiting.sh"
echo ""
echo "2. Input Validation:"
echo "   ./security_tests/test_input_validation.sh"
echo ""
echo "3. JWT Authentication:"
echo "   ./security_tests/test_jwt_authentication.sh"
echo ""
echo "4. Security Monitoring:"
echo "   ./security_tests/test_security_monitoring.sh"
echo ""
echo "5. Session Management:"
echo "   ./security_tests/test_session_management.sh"
echo ""
echo "6. Run All Tests:"
echo "   ./security_tests/run_all_tests.sh"
echo ""

print_success "Security test suite completed!"
