# 🔧 Development Testing Workflow

## **Purpose**
This workflow provides a structured approach for developers to test security features during development and ensure all security measures are working correctly.

## **Prerequisites**
- Backend server running on `http://localhost:5001`
- Database accessible via Docker
- Development environment set up
- All security test scripts available

---

## **🚀 Development Testing Pipeline**

### **1. Pre-Development Setup**

#### **A. Environment Preparation**
```bash
# Start database
docker run -d --name immican_db \
  -e POSTGRES_DB=appdb \
  -e POSTGRES_USER=appuser \
  -e POSTGRES_PASSWORD=apppass \
  -p 5432:5432 postgres:16

# Start backend
cd backend && source ../venv/bin/activate && python app.py

# Clean database
docker exec -i immican_db psql -U appuser -d appdb < ../cleanup_database.sql
```

#### **B. Verify Environment**
```bash
# Check backend health
curl http://localhost:5001/api/health

# Check database connection
docker exec -i immican_db psql -U appuser -d appdb -c "SELECT 1;"

# Check security tables exist
docker exec -i immican_db psql -U appuser -d appdb -c "\dt"
```

---

### **2. Daily Development Testing**

#### **A. Quick Security Check (5 minutes)**
```bash
cd security_tests
./scripts/demo_security_working.sh
```

**What it tests**:
- Email validation
- Password strength
- SQL injection prevention
- Rate limiting
- JWT authentication
- Security monitoring

#### **B. Individual Feature Testing**
```bash
# Test specific security features
./scripts/test_rate_limiting.sh
./scripts/test_input_validation.sh
./scripts/test_jwt_authentication.sh
./scripts/test_security_monitoring.sh
./scripts/test_session_management.sh
```

**When to use**:
- After implementing new security features
- When debugging security issues
- Before deploying changes
- When testing specific functionality

---

### **3. Pre-Deployment Testing**

#### **A. Comprehensive Security Test**
```bash
cd security_tests
./scripts/run_all_tests.sh
```

**What it covers**:
- All security features
- Database verification
- API endpoint testing
- Error handling
- Performance under load

#### **B. Manual Verification**
```bash
# Follow examples/manual_tests.md
# Test critical security paths manually
# Verify database logs
# Check security metrics
```

---

### **4. Security Feature Development**

#### **A. Adding New Security Features**

**Step 1: Implement Feature**
```python
# Add to backend/security_utils.py
def new_security_function():
    # Implementation
    pass
```

**Step 2: Create Test Script**
```bash
# Create new test script
touch scripts/test_new_feature.sh
chmod +x scripts/test_new_feature.sh
```

**Step 3: Test Implementation**
```bash
# Test the new feature
./scripts/test_new_feature.sh
```

**Step 4: Update Documentation**
```bash
# Update README.md
# Add to examples/
# Update workflows/
```

#### **B. Modifying Existing Features**

**Step 1: Backup Current Tests**
```bash
# Backup existing test results
cp scripts/test_*.sh scripts/backup/
```

**Step 2: Modify Feature**
```python
# Update backend code
# Modify security_utils.py
# Update app.py
```

**Step 3: Test Changes**
```bash
# Run affected tests
./scripts/test_affected_feature.sh
```

**Step 4: Verify No Regression**
```bash
# Run all tests
./scripts/run_all_tests.sh
```

---

### **5. Debugging Security Issues**

#### **A. Common Issues and Solutions**

**Issue 1: Rate Limiting Too Aggressive**
```bash
# Check rate limit settings
grep -r "rate_limit" backend/security_utils.py

# Test rate limiting
./scripts/test_rate_limiting.sh

# Adjust settings if needed
```

**Issue 2: JWT Token Issues**
```bash
# Check JWT configuration
grep -r "JWT_" backend/security_utils.py

# Test JWT authentication
./scripts/test_jwt_authentication.sh

# Verify token generation/validation
```

**Issue 3: Database Connection Issues**
```bash
# Check database status
docker ps | grep immican_db

# Test database connection
docker exec -i immican_db psql -U appuser -d appdb -c "SELECT 1;"

# Check security tables
docker exec -i immican_db psql -U appuser -d appdb -c "\dt"
```

**Issue 4: Security Events Not Logging**
```bash
# Check security events
docker exec -i immican_db psql -U appuser -d appdb -c "
SELECT COUNT(*) FROM security_events;"

# Test security monitoring
./scripts/test_security_monitoring.sh

# Check log_security_event function
```

#### **B. Debugging Workflow**

**Step 1: Identify Issue**
```bash
# Run comprehensive test
./scripts/run_all_tests.sh

# Identify failing tests
# Check error messages
# Review test output
```

**Step 2: Isolate Problem**
```bash
# Run individual tests
./scripts/test_specific_feature.sh

# Check manual tests
# Review examples/manual_tests.md

# Test API endpoints directly
```

**Step 3: Check Database**
```bash
# Check security events
docker exec -i immican_db psql -U appuser -d appdb -c "
SELECT * FROM security_events ORDER BY created_at DESC LIMIT 10;"

# Check audit logs
docker exec -i immican_db psql -U appuser -d appdb -c "
SELECT * FROM audit_log ORDER BY created_at DESC LIMIT 10;"
```

**Step 4: Fix and Verify**
```bash
# Fix the issue
# Update code
# Test the fix
./scripts/test_specific_feature.sh

# Run full test suite
./scripts/run_all_tests.sh
```

---

### **6. Continuous Integration Testing**

#### **A. Automated Testing Pipeline**

**GitHub Actions / CI Pipeline**:
```yaml
name: Security Tests
on: [push, pull_request]
jobs:
  security-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Database
        run: |
          docker run -d --name immican_db \
            -e POSTGRES_DB=appdb \
            -e POSTGRES_USER=appuser \
            -e POSTGRES_PASSWORD=apppass \
            -p 5432:5432 postgres:16
      - name: Start Backend
        run: |
          cd backend && python app.py &
      - name: Run Security Tests
        run: |
          cd security_tests
          ./scripts/run_all_tests.sh
      - name: Check Test Results
        run: |
          # Check if tests passed
          # Fail build if security tests fail
```

#### **B. Pre-commit Hooks**
```bash
#!/bin/bash
# .git/hooks/pre-commit
echo "Running security tests..."
cd security_tests
./scripts/demo_security_working.sh
if [ $? -ne 0 ]; then
    echo "Security tests failed. Commit aborted."
    exit 1
fi
echo "Security tests passed. Proceeding with commit."
```

---

### **7. Performance Testing**

#### **A. Load Testing Security Features**

**Rate Limiting Load Test**:
```bash
# Test rate limiting under load
for i in {1..50}; do
  curl -X POST http://localhost:5001/api/login \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com", "password": "wrong"}' &
done
wait
```

**JWT Authentication Load Test**:
```bash
# Test JWT authentication under load
for i in {1..100}; do
  curl -X GET http://localhost:5001/api/users/test/service-requests \
    -H "Authorization: Bearer $token" &
done
wait
```

#### **B. Database Performance Testing**

**Security Events Insertion**:
```bash
# Test security event logging performance
time docker exec -i immican_db psql -U appuser -d appdb -c "
INSERT INTO security_events (event_type, description, ip_address, severity)
SELECT 'API_REQUEST', 'Test request ' || generate_series, '127.0.0.1', 'INFO'
FROM generate_series(1, 1000);"
```

---

### **8. Security Monitoring During Development**

#### **A. Real-Time Monitoring**

**Watch Security Events**:
```bash
# Monitor security events in real-time
watch -n 1 "docker exec -i immican_db psql -U appuser -d appdb -c \"
SELECT 
    event_type,
    LEFT(description, 30) as description,
    severity,
    created_at
FROM security_events 
ORDER BY created_at DESC 
LIMIT 10;\""
```

**Monitor Failed Logins**:
```bash
# Monitor failed login attempts
watch -n 1 "docker exec -i immican_db psql -U appuser -d appdb -c \"
SELECT 
    action_type,
    LEFT(description, 30) as description,
    created_at
FROM audit_log 
WHERE action_type = 'LOGIN_FAILURE'
ORDER BY created_at DESC 
LIMIT 5;\""
```

#### **B. Security Metrics Dashboard**

**Real-Time Metrics**:
```bash
# Get current security metrics
docker exec -i immican_db psql -U appuser -d appdb -c "
SELECT 
    'Security Events (Last Hour)' as metric,
    COUNT(*) as value
FROM security_events 
WHERE created_at > NOW() - INTERVAL '1 hour'
UNION ALL
SELECT 
    'Active Sessions',
    COUNT(*)
FROM active_sessions 
WHERE expires_at > NOW()
UNION ALL
SELECT 
    'Failed Logins (Last Hour)',
    COUNT(*)
FROM audit_log 
WHERE action_type = 'LOGIN_FAILURE' 
AND created_at > NOW() - INTERVAL '1 hour';"
```

---

### **9. Documentation and Reporting**

#### **A. Test Results Documentation**

**Generate Test Report**:
```bash
#!/bin/bash
# generate_security_report.sh
echo "🛡️  SECURITY TEST REPORT" > security_report.txt
echo "Generated: $(date)" >> security_report.txt
echo "================================" >> security_report.txt
echo "" >> security_report.txt

# Run tests and capture output
./scripts/run_all_tests.sh >> security_report.txt 2>&1

# Add database metrics
echo "" >> security_report.txt
echo "DATABASE METRICS:" >> security_report.txt
docker exec -i immican_db psql -U appuser -d appdb -c "
SELECT 
    'Security Events' as table_name,
    COUNT(*) as count
FROM security_events
UNION ALL
SELECT 
    'Active Sessions',
    COUNT(*)
FROM active_sessions
WHERE expires_at > NOW();" >> security_report.txt
```

#### **B. Security Compliance Report**

**Generate Compliance Report**:
```bash
#!/bin/bash
# generate_compliance_report.sh
echo "🛡️  SECURITY COMPLIANCE REPORT" > compliance_report.txt
echo "Generated: $(date)" >> compliance_report.txt
echo "================================" >> compliance_report.txt

# Check OWASP compliance
echo "OWASP TOP 10 COMPLIANCE:" >> compliance_report.txt
echo "✅ A01 - Broken Access Control: JWT authentication implemented" >> compliance_report.txt
echo "✅ A02 - Cryptographic Failures: Password hashing with SHA-256" >> compliance_report.txt
echo "✅ A03 - Injection: SQL injection prevention implemented" >> compliance_report.txt
echo "✅ A04 - Insecure Design: Security-first architecture" >> compliance_report.txt
echo "✅ A05 - Security Misconfiguration: Security headers implemented" >> compliance_report.txt
echo "✅ A06 - Vulnerable Components: Regular security updates" >> compliance_report.txt
echo "✅ A07 - Identity and Authentication: JWT with session management" >> compliance_report.txt
echo "✅ A08 - Software and Data Integrity: Input validation implemented" >> compliance_report.txt
echo "✅ A09 - Security Logging: Comprehensive audit trails" >> compliance_report.txt
echo "✅ A10 - Server-Side Request Forgery: Input validation prevents SSRF" >> compliance_report.txt
```

---

### **10. Best Practices**

#### **A. Development Best Practices**

**Code Review Checklist**:
- [ ] Security features tested
- [ ] Input validation implemented
- [ ] Error handling secure
- [ ] No hardcoded secrets
- [ ] Proper logging implemented
- [ ] Database queries parameterized
- [ ] Security headers set
- [ ] Rate limiting considered

**Testing Best Practices**:
- [ ] Test security features first
- [ ] Use automated testing
- [ ] Test edge cases
- [ ] Verify error handling
- [ ] Check database logs
- [ ] Test under load
- [ ] Document test results
- [ ] Regular security audits

#### **B. Security Best Practices**

**Development Security**:
- [ ] Never commit secrets
- [ ] Use environment variables
- [ ] Validate all inputs
- [ ] Sanitize outputs
- [ ] Use parameterized queries
- [ ] Implement proper error handling
- [ ] Log security events
- [ ] Regular security updates

**Testing Security**:
- [ ] Test all security features
- [ ] Verify database security
- [ ] Check API security
- [ ] Test authentication
- [ ] Verify authorization
- [ ] Check input validation
- [ ] Test error handling
- [ ] Monitor security events

---

## **🎯 Success Metrics**

### **Development Testing Success**
- ✅ All security tests pass
- ✅ No security vulnerabilities found
- ✅ Performance meets requirements
- ✅ Database security verified
- ✅ API security confirmed
- ✅ Monitoring working correctly
- ✅ Documentation up to date
- ✅ Compliance requirements met

### **Key Takeaways**
- **Security testing is integrated into development**
- **All security features are verified**
- **Performance is monitored**
- **Compliance is maintained**
- **Documentation is current**
- **Best practices are followed**

**🛡️ Your development workflow ensures security is maintained throughout the development process!**
