# 🛡️ Individual Security Feature Tests

This directory contains individual test scripts for each security feature, allowing you to test and demonstrate specific security aspects separately.

## 📋 Available Tests

### **1. Rate Limiting Test** (`test_rate_limiting.sh`)
**Purpose**: Tests rate limiting functionality to prevent brute force attacks

**What it tests**:
- ✅ Login endpoint rate limiting (10 requests per 5 minutes)
- ✅ Registration endpoint (not rate limited)
- ✅ Different IP addresses have separate rate limits
- ✅ 429 status code when limit exceeded
- ✅ Rate limit data stored in database

**Usage**:
```bash
./security_tests/test_rate_limiting.sh
```

**Expected Output**:
- First 10 requests: 401 Unauthorized (expected)
- 11th request: 429 Rate Limit Exceeded
- Database shows rate limit entries

---

### **2. Input Validation Test** (`test_input_validation.sh`)
**Purpose**: Tests input validation and sanitization to prevent injection attacks

**What it tests**:
- ✅ Email format validation (valid/invalid emails)
- ✅ Password strength requirements
- ✅ SQL injection prevention
- ✅ XSS attack prevention
- ✅ Command injection prevention
- ✅ Input length limits
- ✅ Service type validation

**Usage**:
```bash
./security_tests/test_input_validation.sh
```

**Expected Output**:
- Valid inputs accepted
- Invalid inputs rejected with error messages
- Injection attempts blocked and logged

---

### **3. JWT Authentication Test** (`test_jwt_authentication.sh`)
**Purpose**: Tests JWT token authentication and session management

**What it tests**:
- ✅ User registration and login
- ✅ JWT token generation (access + refresh)
- ✅ Protected endpoint access with valid token
- ✅ Rejection of requests without/invalid tokens
- ✅ Token refresh functionality
- ✅ Session management in database
- ✅ Logout functionality

**Usage**:
```bash
./security_tests/test_jwt_authentication.sh
```

**Expected Output**:
- Successful login returns JWT tokens
- Protected endpoints require valid tokens
- Token refresh works correctly
- Sessions tracked in database

---

### **4. Security Monitoring Test** (`test_security_monitoring.sh`)
**Purpose**: Tests security event logging and monitoring capabilities

**What it tests**:
- ✅ Real-time security event logging
- ✅ IP address tracking and analysis
- ✅ Suspicious activity detection
- ✅ Security metrics calculation
- ✅ Event type classification
- ✅ Severity level assignment
- ✅ Audit log integration

**Usage**:
```bash
./security_tests/test_security_monitoring.sh
```

**Expected Output**:
- All API requests logged with metadata
- Suspicious activities detected and flagged
- Security metrics calculated in real-time
- Database shows comprehensive event logs

---

### **5. Session Management Test** (`test_session_management.sh`)
**Purpose**: Tests session management and JWT token handling

**What it tests**:
- ✅ Session creation and storage
- ✅ Multiple concurrent sessions
- ✅ Session validation and expiration
- ✅ Session destruction on logout
- ✅ Session hijacking prevention
- ✅ Activity tracking and monitoring
- ✅ Security headers and protection

**Usage**:
```bash
./security_tests/test_session_management.sh
```

**Expected Output**:
- Sessions created on login
- Multiple sessions supported per user
- Sessions destroyed on logout
- Activity tracked and updated

---

## 🚀 Running Tests

### **Run All Tests**
```bash
./security_tests/run_all_tests.sh
```

### **Run Individual Tests**
```bash
# Rate limiting
./security_tests/test_rate_limiting.sh

# Input validation
./security_tests/test_input_validation.sh

# JWT authentication
./security_tests/test_jwt_authentication.sh

# Security monitoring
./security_tests/test_security_monitoring.sh

# Session management
./security_tests/test_session_management.sh
```

### **Run Tests in Sequence**
```bash
cd security_tests
./test_rate_limiting.sh
./test_input_validation.sh
./test_jwt_authentication.sh
./test_security_monitoring.sh
./test_session_management.sh
```

## 📊 What Each Test Demonstrates

### **For Employers - Individual Feature Focus**

**Rate Limiting Test**:
- Shows how the system prevents brute force attacks
- Demonstrates IP-based rate limiting
- Shows 429 status codes for rate limit exceeded
- Proves rate limit data is stored in database

**Input Validation Test**:
- Shows comprehensive input sanitization
- Demonstrates injection attack prevention
- Proves XSS and SQL injection blocking
- Shows password strength enforcement

**JWT Authentication Test**:
- Shows secure token-based authentication
- Demonstrates protected endpoint access
- Proves token refresh functionality
- Shows session management capabilities

**Security Monitoring Test**:
- Shows real-time security event logging
- Demonstrates threat detection capabilities
- Proves comprehensive audit trails
- Shows security metrics calculation

**Session Management Test**:
- Shows secure session handling
- Demonstrates concurrent session support
- Proves session destruction on logout
- Shows activity tracking and monitoring

## 🔍 Database Verification

After running each test, you can verify the results in the database:

```bash
# Check security events
docker exec -i immican_db psql -U appuser -d appdb -c "SELECT * FROM security_events ORDER BY created_at DESC LIMIT 10;"

# Check active sessions
docker exec -i immican_db psql -U appuser -d appdb -c "SELECT * FROM active_sessions ORDER BY created_at DESC;"

# Check rate limits
docker exec -i immican_db psql -U appuser -d appdb -c "SELECT * FROM rate_limits ORDER BY created_at DESC;"

# Check suspicious activities
docker exec -i immican_db psql -U appuser -d appdb -c "SELECT * FROM suspicious_activities ORDER BY created_at DESC;"
```

## 🎯 Benefits of Individual Testing

### **For Development**
- **Focused Testing**: Test specific security features in isolation
- **Debugging**: Easier to identify issues with specific features
- **Development**: Test new security features individually
- **Verification**: Confirm each security measure works correctly

### **For Employers**
- **Demonstration**: Show specific security capabilities
- **Understanding**: Explain how each security feature works
- **Confidence**: Prove each security measure is functional
- **Compliance**: Demonstrate specific security requirements

### **For Security Audits**
- **Comprehensive Coverage**: Test all security aspects
- **Documentation**: Each test provides evidence of security
- **Compliance**: Meet security audit requirements
- **Verification**: Prove security measures are working

## 🛡️ Security Features Covered

✅ **Rate Limiting**: Prevents brute force and DoS attacks
✅ **Input Validation**: Blocks injection and XSS attacks  
✅ **JWT Authentication**: Secures API endpoints
✅ **Security Monitoring**: Logs and detects threats
✅ **Session Management**: Handles user sessions securely
✅ **Database Persistence**: All security data stored
✅ **Real-time Detection**: Immediate threat response
✅ **Comprehensive Logging**: Complete audit trails

Each test provides **complete visibility** into how the security features work and demonstrates **enterprise-grade security** implementation.
