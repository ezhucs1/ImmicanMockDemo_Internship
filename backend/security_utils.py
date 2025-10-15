"""
Security utilities for input validation, sanitization, and security headers
"""
import re
import html
import hashlib
import secrets
import jwt
from functools import wraps
from flask import request, jsonify, g
from datetime import datetime, timedelta
import time
import os

# ============ JWT CONFIGURATION ============

# JWT Secret Key (in production, use environment variable)
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-super-secret-jwt-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24  # Token expires in 24 hours
JWT_REFRESH_EXPIRATION_DAYS = 7  # Refresh token expires in 7 days

# ============ JWT TOKEN MANAGEMENT ============

def generate_jwt_token(user_id, user_type, email):
    """Generate JWT access token"""
    payload = {
        'user_id': user_id,
        'user_type': user_type,
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow(),
        'type': 'access'
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def generate_refresh_token(user_id):
    """Generate JWT refresh token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=JWT_REFRESH_EXPIRATION_DAYS),
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None, "Token has expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"

def get_token_from_request():
    """Extract JWT token from request headers"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return None

# ============ JWT AUTHENTICATION DECORATOR ============

def jwt_required(f):
    """Decorator to require JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()
        
        if not token:
            return jsonify({
                "ok": False,
                "msg": "Authentication token is required"
            }), 401
        
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({
                "ok": False,
                "msg": "Invalid or expired token"
            }), 401
        
        # Store user info in Flask's g object for use in the route
        g.current_user = {
            'user_id': payload['user_id'],
            'user_type': payload['user_type'],
            'email': payload['email']
        }
        
        return f(*args, **kwargs)
    return decorated_function

def jwt_optional(f):
    """Decorator for optional JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()
        
        if token:
            payload = verify_jwt_token(token)
            if payload:
                g.current_user = {
                    'user_id': payload['user_id'],
                    'user_type': payload['user_type'],
                    'email': payload['email']
                }
            else:
                g.current_user = None
        else:
            g.current_user = None
        
        return f(*args, **kwargs)
    return decorated_function

# ============ INPUT VALIDATION ============

def validate_email(email):
    """Validate email format"""
    if not email or not isinstance(email, str):
        return False
    
    email = email.strip().lower()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password_strength(password):
    """Validate password strength"""
    if not password or not isinstance(password, str):
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    # Check for common weak passwords
    weak_passwords = [
        'password', '123456', '123456789', 'qwerty', 'abc123',
        'password123', 'admin', 'letmein', 'welcome', 'monkey'
    ]
    
    if password.lower() in weak_passwords:
        return False, "Password is too common. Please choose a stronger password"
    
    return True, "Password is strong"

def sanitize_input(text, max_length=1000):
    """Sanitize user input to prevent XSS and injection attacks"""
    if not text or not isinstance(text, str):
        return ""
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    # HTML escape to prevent XSS
    text = html.escape(text)
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    
    return text.strip()

def validate_name(name, field_name="Name"):
    """Validate name fields"""
    if not name or not isinstance(name, str):
        return False, f"{field_name} is required"
    
    name = name.strip()
    
    if len(name) < 1:
        return False, f"{field_name} cannot be empty"
    
    if len(name) > 100:
        return False, f"{field_name} must be less than 100 characters"
    
    # Allow letters, spaces, hyphens, and apostrophes
    if not re.match(r"^[a-zA-Z\s\-']+$", name):
        return False, f"{field_name} can only contain letters, spaces, hyphens, and apostrophes"
    
    return True, "Valid"

def validate_phone(phone):
    """Validate phone number"""
    if not phone:
        return True, "Valid"  # Phone is optional
    
    if not isinstance(phone, str):
        return False, "Phone number must be a string"
    
    phone = phone.strip()
    
    # Allow various phone formats
    pattern = r'^[\+]?[1-9]?[\d\s\-\(\)\.]{7,15}$'
    if not re.match(pattern, phone):
        return False, "Invalid phone number format"
    
    return True, "Valid"

def validate_service_type(service_type):
    """Validate service type"""
    valid_types = ['Legal', 'Medical', 'Education', 'Employment', 'Housing', 'Other']
    
    if not service_type or not isinstance(service_type, str):
        return False, "Service type is required"
    
    if service_type not in valid_types:
        return False, f"Service type must be one of: {', '.join(valid_types)}"
    
    return True, "Valid"

def validate_priority(priority):
    """Validate priority level"""
    valid_priorities = ['LOW', 'MEDIUM', 'HIGH', 'URGENT']
    
    if not priority or not isinstance(priority, str):
        return False, "Priority is required"
    
    if priority not in valid_priorities:
        return False, f"Priority must be one of: {', '.join(valid_priorities)}"
    
    return True, "Valid"

# ============ RATE LIMITING ============

# In-memory rate limiting store (in production, use Redis)
rate_limit_store = {}

def rate_limit(max_requests=10, window_seconds=60, key_func=None):
    """
    Rate limiting decorator
    
    Args:
        max_requests: Maximum number of requests allowed
        window_seconds: Time window in seconds
        key_func: Function to generate rate limit key (defaults to IP address)
    
    Note: Registration endpoints should NOT use rate limiting to allow legitimate users
    to register without restrictions. Rate limiting is primarily for login and API endpoints.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate rate limit key
            if key_func:
                key = key_func()
            else:
                key = request.remote_addr or 'unknown'
            
            # Get current time
            now = time.time()
            
            # Initialize or get existing requests for this key
            if key not in rate_limit_store:
                rate_limit_store[key] = []
            
            # Remove old requests outside the window
            rate_limit_store[key] = [
                req_time for req_time in rate_limit_store[key]
                if now - req_time < window_seconds
            ]
            
            # Check if limit exceeded
            if len(rate_limit_store[key]) >= max_requests:
                return jsonify({
                    "ok": False,
                    "msg": f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds."
                }), 429
            
            # Add current request
            rate_limit_store[key].append(now)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ============ SECURITY HEADERS ============

def add_security_headers(response):
    """Add security headers to response"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' ws: wss:;"
    return response

# ============ PASSWORD SECURITY ============

def generate_salt():
    """Generate a random salt"""
    return secrets.token_hex(32)

def hash_password_secure(password, salt=None):
    """Hash password with salt using SHA-256 (improved version)"""
    if salt is None:
        salt = generate_salt()
    
    # Combine password and salt
    salted_password = password + salt
    
    # Hash multiple times to make it more secure
    hash_value = salted_password
    for _ in range(1000):  # 1000 iterations
        hash_value = hashlib.sha256(hash_value.encode()).hexdigest()
    
    return hash_value, salt

def verify_password_secure(password, hashed_password, salt):
    """Verify password against hash and salt"""
    computed_hash, _ = hash_password_secure(password, salt)
    return computed_hash == hashed_password

# ============ VALIDATION DECORATORS ============

def validate_json_input(required_fields=None, optional_fields=None):
    """
    Decorator to validate JSON input
    
    Args:
        required_fields: List of required field names
        optional_fields: List of optional field names with their validators
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = request.get_json(force=True) or {}
                
                # Validate required fields
                if required_fields:
                    for field in required_fields:
                        if field not in data or not data[field]:
                            return jsonify({
                                "ok": False,
                                "msg": f"Field '{field}' is required"
                            }), 400
                
                # Validate optional fields
                if optional_fields:
                    for field, validator in optional_fields.items():
                        if field in data and data[field]:
                            is_valid, message = validator(data[field])
                            if not is_valid:
                                return jsonify({
                                    "ok": False,
                                    "msg": f"Invalid {field}: {message}"
                                }), 400
                
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    "ok": False,
                    "msg": "Invalid JSON input"
                }), 400
        return decorated_function
    return decorator

# ============ ADVANCED LOGGING & MONITORING ============

# Database connection for security logging (will be injected from app.py)
db_engine = None

def set_db_engine(engine):
    """Set the database engine for security logging"""
    global db_engine
    db_engine = engine

def log_security_event(event_type, description, user_id=None, ip_address=None, severity='INFO'):
    """Enhanced security event logging to database"""
    from sqlalchemy import text
    import uuid
    
    timestamp = datetime.now()
    ip = ip_address or (request.remote_addr if request else 'unknown')
    user_agent = request.headers.get('User-Agent', 'unknown') if request else 'unknown'
    request_path = request.path if request else 'unknown'
    request_method = request.method if request else 'unknown'
    
    log_entry = {
        'id': str(uuid.uuid4()),
        'event_type': event_type,
        'description': description,
        'user_id': user_id,
        'ip_address': ip,
        'user_agent': user_agent,
        'severity': severity,
        'request_path': request_path,
        'request_method': request_method,
        'created_at': timestamp
    }
    
    # Store in database if engine is available
    if db_engine:
        try:
            with db_engine.begin() as conn:
                conn.execute(text("""
                    INSERT INTO security_events (id, event_type, description, user_id, ip_address, 
                                               user_agent, severity, request_path, request_method, created_at)
                    VALUES (:id, :event_type, :description, :user_id, :ip_address, :user_agent, 
                           :severity, :request_path, :request_method, :created_at)
                """), log_entry)
        except Exception as e:
            print(f"Failed to log security event to database: {e}", flush=True)
    
    # Check for suspicious patterns
    check_suspicious_activity(log_entry)
    
    # Log to console with severity
    severity_emoji = {
        'INFO': 'ℹ️',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🚨'
    }
    emoji = severity_emoji.get(severity, 'ℹ️')
    print(f"{emoji} SECURITY EVENT [{severity}]: {event_type} - {description}", flush=True)
    
    return log_entry

def check_suspicious_activity(log_entry):
    """Detect suspicious activity patterns using database"""
    from sqlalchemy import text
    import uuid
    
    if not db_engine:
        return
    
    ip = log_entry['ip_address']
    event_type = log_entry['event_type']
    
    try:
        with db_engine.begin() as conn:
            # Count recent events from same IP (last 5 minutes)
            recent_events_result = conn.execute(text("""
                SELECT event_type, COUNT(*) as count
                FROM security_events 
                WHERE ip_address = :ip AND created_at > NOW() - INTERVAL '5 minutes'
                GROUP BY event_type
            """), {"ip": ip}).fetchall()
            
            # Count total recent events
            total_events_result = conn.execute(text("""
                SELECT COUNT(*) as total
                FROM security_events 
                WHERE ip_address = :ip AND created_at > NOW() - INTERVAL '5 minutes'
            """), {"ip": ip}).fetchone()
            
            total_recent_events = total_events_result.total if total_events_result else 0
            
            # Detect suspicious patterns
            suspicious_patterns = []
            
            # Check for specific event types
            for row in recent_events_result:
                if row.event_type == 'LOGIN_FAILURE' and row.count >= 5:
                    suspicious_patterns.append(f"Multiple failed logins ({row.count}) from IP {ip}")
                elif row.event_type == 'REGISTRATION_FAILURE' and row.count >= 3:
                    suspicious_patterns.append(f"Multiple registration failures ({row.count}) from IP {ip}")
            
            # High frequency of requests
            if total_recent_events >= 20:
                suspicious_patterns.append(f"High request frequency ({total_recent_events} requests in 5 minutes) from IP {ip}")
            
            # Log suspicious activities to database
            if suspicious_patterns:
                for pattern in suspicious_patterns:
                    suspicious_activity = {
                        'id': str(uuid.uuid4()),
                        'pattern': pattern,
                        'ip_address': ip,
                        'event_count': total_recent_events,
                        'severity': 'HIGH',
                        'description': f"Suspicious activity detected: {pattern}",
                        'created_at': datetime.now()
                    }
                    
                    conn.execute(text("""
                        INSERT INTO suspicious_activities (id, pattern, ip_address, event_count, severity, description, created_at)
                        VALUES (:id, :pattern, :ip_address, :event_count, :severity, :description, :created_at)
                    """), suspicious_activity)
                    
                    print(f"🚨 SUSPICIOUS ACTIVITY DETECTED: {pattern}", flush=True)
                    
    except Exception as e:
        print(f"Failed to check suspicious activity: {e}", flush=True)

def get_security_metrics():
    """Get security metrics for monitoring"""
    now = datetime.now()
    last_hour = now - timedelta(hours=1)
    last_day = now - timedelta(days=1)
    
    recent_events = [e for e in security_events if datetime.fromisoformat(e['timestamp']) > last_hour]
    daily_events = [e for e in security_events if datetime.fromisoformat(e['timestamp']) > last_day]
    
    metrics = {
        'total_events': len(security_events),
        'events_last_hour': len(recent_events),
        'events_last_day': len(daily_events),
        'suspicious_activities': len(suspicious_activities),
        'recent_suspicious': len([a for a in suspicious_activities if datetime.fromisoformat(a['timestamp']) > last_hour]),
        'top_ips': get_top_ips(recent_events),
        'event_types': get_event_type_counts(recent_events)
    }
    
    return metrics

def get_top_ips(events, limit=10):
    """Get top IP addresses by event count"""
    ip_counts = {}
    for event in events:
        ip = event['ip_address']
        ip_counts[ip] = ip_counts.get(ip, 0) + 1
    
    return sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:limit]

def get_event_type_counts(events):
    """Get event type counts"""
    type_counts = {}
    for event in events:
        event_type = event['event_type']
        type_counts[event_type] = type_counts.get(event_type, 0) + 1
    
    return type_counts

def log_api_request():
    """Log API request for monitoring"""
    if request:
        log_security_event(
            'API_REQUEST',
            f"{request.method} {request.path}",
            severity='INFO'
        )

# ============ SESSION MANAGEMENT ============

def create_session(user_id, user_type, email):
    """Create a new session in database"""
    from sqlalchemy import text
    import uuid
    
    session_id = str(uuid.uuid4())
    created_at = datetime.now()
    expires_at = created_at + timedelta(hours=24)  # 24 hour session
    ip_address = request.remote_addr if request else 'unknown'
    user_agent = request.headers.get('User-Agent', 'unknown') if request else 'unknown'
    
    if db_engine:
        try:
            with db_engine.begin() as conn:
                conn.execute(text("""
                    INSERT INTO active_sessions (id, user_id, user_type, email, ip_address, user_agent, created_at, last_activity, expires_at)
                    VALUES (:id, :user_id, :user_type, :email, :ip_address, :user_agent, :created_at, :last_activity, :expires_at)
                """), {
                    'id': session_id,
                    'user_id': user_id,
                    'user_type': user_type,
                    'email': email,
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'created_at': created_at,
                    'last_activity': created_at,
                    'expires_at': expires_at
                })
        except Exception as e:
            print(f"Failed to create session in database: {e}", flush=True)
            return None
    
    # Log session creation
    log_security_event(
        'SESSION_CREATED',
        f"New session created for user {email}",
        user_id=user_id,
        severity='INFO'
    )
    
    return session_id

def validate_session(session_id):
    """Validate session and update last activity in database"""
    from sqlalchemy import text
    
    if not db_engine:
        return None
    
    try:
        with db_engine.begin() as conn:
            # Get session from database
            session_result = conn.execute(text("""
                SELECT id, user_id, user_type, email, created_at, expires_at
                FROM active_sessions 
                WHERE id = :session_id AND expires_at > NOW()
            """), {"session_id": session_id}).fetchone()
            
            if not session_result:
                return None
            
            # Update last activity
            conn.execute(text("""
                UPDATE active_sessions 
                SET last_activity = NOW() 
                WHERE id = :session_id
            """), {"session_id": session_id})
            
            return {
                'id': session_result.id,
                'user_id': session_result.user_id,
                'user_type': session_result.user_type,
                'email': session_result.email,
                'created_at': session_result.created_at,
                'expires_at': session_result.expires_at
            }
            
    except Exception as e:
        print(f"Failed to validate session: {e}", flush=True)
        return None

def destroy_session(session_id):
    """Destroy a session in database"""
    from sqlalchemy import text
    
    if not db_engine:
        return
    
    try:
        with db_engine.begin() as conn:
            # Get session info before deleting
            session_result = conn.execute(text("""
                SELECT user_id, email FROM active_sessions WHERE id = :session_id
            """), {"session_id": session_id}).fetchone()
            
            if session_result:
                # Delete session
                conn.execute(text("""
                    DELETE FROM active_sessions WHERE id = :session_id
                """), {"session_id": session_id})
                
                # Log session destruction
                log_security_event(
                    'SESSION_DESTROYED',
                    f"Session destroyed for user {session_result.email}",
                    user_id=session_result.user_id,
                    severity='INFO'
                )
                
    except Exception as e:
        print(f"Failed to destroy session: {e}", flush=True)

def cleanup_expired_sessions():
    """Clean up expired sessions using database function"""
    if not db_engine:
        return 0
    
    try:
        with db_engine.begin() as conn:
            result = conn.execute(text("SELECT cleanup_expired_sessions()")).fetchone()
            deleted_count = result[0] if result else 0
            
            if deleted_count > 0:
                log_security_event(
                    'SESSION_CLEANUP',
                    f"Cleaned up {deleted_count} expired sessions",
                    severity='INFO'
                )
            
            return deleted_count
            
    except Exception as e:
        print(f"Failed to cleanup expired sessions: {e}", flush=True)
        return 0

def get_active_sessions_count():
    """Get count of active sessions from database"""
    from sqlalchemy import text
    
    if not db_engine:
        return 0
    
    try:
        with db_engine.begin() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) as count FROM active_sessions WHERE expires_at > NOW()
            """)).fetchone()
            return result.count if result else 0
    except Exception as e:
        print(f"Failed to get active sessions count: {e}", flush=True)
        return 0
