# app.py
import os, uuid, datetime, sys
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from sqlalchemy import create_engine, text
import hashlib
from dotenv import load_dotenv
import secrets
import base64

# Email verification imports (commented out for now)
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
from security_utils import (
    validate_email, validate_password_strength, sanitize_input,
    validate_name, validate_phone, validate_service_type, validate_priority,
    rate_limit, add_security_headers, hash_password_secure, verify_password_secure,
    validate_json_input, log_security_event,
    generate_jwt_token, generate_refresh_token, verify_jwt_token,
    jwt_required, jwt_optional, get_token_from_request,
    create_session, validate_session, destroy_session, cleanup_expired_sessions,
    get_security_metrics, log_api_request, get_active_sessions_count,
    set_db_engine
)

print(">> Loading .env", flush=True)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
PORT = int(os.getenv("PORT", "5001"))

if not DATABASE_URL:
    print("!! DATABASE_URL is missing in .env", file=sys.stderr, flush=True)
    sys.exit(1)

print(f">> Connecting to DB: {DATABASE_URL}", flush=True)
engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True)

# Initialize security utilities with database engine
set_db_engine(engine)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Add security headers to all responses
@app.after_request
def after_request(response):
    return add_security_headers(response)

# Log all API requests for monitoring
@app.before_request
def before_request():
    log_api_request()

# Simple password hashing function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hashlib.sha256(password.encode()).hexdigest() == hashed

# ============ EMAIL VERIFICATION FUNCTIONS ============

def generate_verification_token():
    """Generate a secure verification token"""
    return secrets.token_urlsafe(32)

def create_verification_token(user_id):
    """Create a new email verification token for a user"""
    token = generate_verification_token()
    expires_at = datetime.datetime.now() + datetime.timedelta(hours=24)
    
    try:
        with engine.begin() as conn:
            # Clean up old tokens for this user
            conn.execute(text("""
                DELETE FROM email_verification_tokens 
                WHERE user_id = :user_id AND (used = TRUE OR expires_at < NOW())
            """), {"user_id": user_id})
            
            # Insert new token
            conn.execute(text("""
                INSERT INTO email_verification_tokens (user_id, token, expires_at)
                VALUES (:user_id, :token, :expires_at)
            """), {
                "user_id": user_id,
                "token": token,
                "expires_at": expires_at
            })
            
        return token
    except Exception as e:
        print(f"Error creating verification token: {e}")
        return None

def send_verification_email(email, token, user_name=""):
    """
    Send verification email to user
    This function is commented out for now - implement when ready to send real emails
    """
    # EMAIL SENDING CODE (COMMENTED OUT)
    # Uncomment and configure when ready to send real emails
    
    # try:
    #     # Email configuration (set these in your .env file)
    #     SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    #     SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    #     SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    #     SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    #     FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@immican.com")
    #     
    #     # Create verification URL
    #     verification_url = f"http://localhost:5173/verify-email?token={token}"
    #     
    #     # Create email content
    #     subject = "Verify Your immiCan Account"
    #     
    #     html_body = f"""
    #     <html>
    #     <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    #         <h2 style="color: #4F46E5;">Welcome to immiCan!</h2>
    #         <p>Hello {user_name or 'there'},</p>
    #         <p>Thank you for registering with immiCan. To complete your registration and start using your account, please verify your email address by clicking the button below:</p>
    #         <div style="text-align: center; margin: 30px 0;">
    #             <a href="{verification_url}" style="background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Verify Email Address</a>
    #         </div>
    #         <p>Or copy and paste this link into your browser:</p>
    #         <p style="word-break: break-all; color: #666;">{verification_url}</p>
    #         <p>This verification link will expire in 24 hours.</p>
    #         <p>If you didn't create an account with immiCan, please ignore this email.</p>
    #         <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
    #         <p style="color: #666; font-size: 12px;">
    #             This is an automated message from immiCan. Please do not reply to this email.
    #         </p>
    #     </body>
    #     </html>
    #     """
    #     
    #     # Create message
    #     msg = MIMEMultipart('alternative')
    #     msg['Subject'] = subject
    #     msg['From'] = FROM_EMAIL
    #     msg['To'] = email
    #     
    #     # Add HTML content
    #     html_part = MIMEText(html_body, 'html')
    #     msg.attach(html_part)
    #     
    #     # Send email
    #     with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
    #         server.starttls()
    #         server.login(SMTP_USERNAME, SMTP_PASSWORD)
    #         server.send_message(msg)
    #     
    #     print(f"Verification email sent to {email}")
    #     return True
    #     
    # except Exception as e:
    #     print(f"Error sending verification email: {e}")
    #     return False
    
    # For now, just print the verification URL (remove this when implementing real emails)
    verification_url = f"http://localhost:5173/verify-email?token={token}"
    print(f"VERIFICATION EMAIL (not sent): {email}")
    print(f"Verification URL: {verification_url}")
    return True

def verify_email_token(token):
    """Verify an email verification token"""
    try:
        with engine.begin() as conn:
            # Find the token
            result = conn.execute(text("""
                SELECT user_id, expires_at, used
                FROM email_verification_tokens
                WHERE token = :token
            """), {"token": token}).fetchone()
            
            if not result:
                return False, "Invalid verification token"
            
            user_id, expires_at, used = result
            
            if used:
                return False, "Token has already been used"
            
            if expires_at < datetime.datetime.now():
                return False, "Token has expired"
            
            # Mark token as used and verify user's email
            conn.execute(text("""
                UPDATE email_verification_tokens 
                SET used = TRUE, used_at = NOW()
                WHERE token = :token
            """), {"token": token})
            
            conn.execute(text("""
                UPDATE users_login 
                SET email_verified = TRUE
                WHERE id = :user_id
            """), {"user_id": user_id})
            
            return True, "Email verified successfully"
            
    except Exception as e:
        print(f"Error verifying email token: {e}")
        return False, "Error verifying token"

# ============ WEBSOCKET EVENTS ============

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

@socketio.on('join_conversation')
def handle_join_conversation(data):
    conversation_id = data.get('conversation_id')
    user_id = data.get('user_id')
    
    if conversation_id and user_id:
        # Verify user has access to this conversation
        with engine.begin() as conn:
            conv = conn.execute(text("""
                SELECT c.user_id, c.provider_id, sp.user_id as provider_user_id
                FROM conversations c
                LEFT JOIN service_providers sp ON c.provider_id = sp.id
                WHERE c.id = :conv_id
            """), {"conv_id": conversation_id}).fetchone()
            
            if conv and (conv.user_id == user_id or conv.provider_user_id == user_id):
                join_room(f"conversation_{conversation_id}")
                emit('joined_conversation', {'conversation_id': conversation_id})
                print(f"User {user_id} joined conversation {conversation_id}")
            else:
                print(f"Authorization failed for user {user_id} in conversation {conversation_id}")
                print(f"Conversation user_id: {conv.user_id if conv else 'None'}")
                print(f"Conversation provider_user_id: {conv.provider_user_id if conv else 'None'}")
                emit('error', {'message': 'Unauthorized to join this conversation'})

@socketio.on('leave_conversation')
def handle_leave_conversation(data):
    conversation_id = data.get('conversation_id')
    if conversation_id:
        leave_room(f"conversation_{conversation_id}")
        emit('left_conversation', {'conversation_id': conversation_id})

@socketio.on('send_message')
def handle_send_message(data):
    conversation_id = data.get('conversation_id')
    sender_id = data.get('sender_id')
    sender_type = data.get('sender_type')
    message_text = data.get('message_text')
    
    if not all([conversation_id, sender_id, sender_type, message_text]):
        emit('error', {'message': 'Missing required fields'})
        return
    
    try:
        with engine.begin() as conn:
            # Verify conversation exists and sender is authorized
            conv = conn.execute(text("""
                SELECT c.user_id, c.provider_id, sp.user_id as provider_user_id
                FROM conversations c
                LEFT JOIN service_providers sp ON c.provider_id = sp.id
                WHERE c.id = :conv_id
            """), {"conv_id": conversation_id}).fetchone()
            
            if not conv:
                emit('error', {'message': 'Conversation not found'})
                return
            
            # Check authorization
            if sender_type == 'CLIENT' and conv.user_id != sender_id:
                print(f"Client authorization failed: sender_id={sender_id}, conv.user_id={conv.user_id}")
                emit('error', {'message': 'Unauthorized'})
                return
            elif sender_type == 'PROVIDER' and conv.provider_user_id != sender_id:
                print(f"Provider authorization failed: sender_id={sender_id}, conv.provider_user_id={conv.provider_user_id}")
                emit('error', {'message': 'Unauthorized'})
                return
            
            # Insert message
            message_id = str(uuid.uuid4())
            conn.execute(text("""
                INSERT INTO messages (id, conversation_id, sender_id, sender_type, message_text, created_date)
                VALUES (:id, :conversation_id, :sender_id, :sender_type, :message_text, NOW())
            """), {
                "id": message_id,
                "conversation_id": conversation_id,
                "sender_id": sender_id,
                "sender_type": sender_type,
                "message_text": message_text
            })
            
            # Log message
            conn.execute(text("""
                INSERT INTO audit_log (action_type, description, created_by, created_at)
                VALUES ('MESSAGE_SENT', 'Message sent in conversation: ' || :conv_id, :sender_id, NOW())
            """), {"conv_id": conversation_id, "sender_id": sender_id})
        
        # Broadcast message to all users in the conversation room
        message_data = {
            'id': message_id,
            'conversation_id': conversation_id,
            'sender_id': sender_id,
            'sender_type': sender_type,
            'message_text': message_text,
            'created_date': datetime.datetime.utcnow().isoformat(),
            'is_read': False
        }
        
        socketio.emit('new_message', message_data, room=f"conversation_{conversation_id}")
        print(f"Message sent in conversation {conversation_id} by {sender_type} {sender_id}")
        
    except Exception as e:
        print(f"Error sending message: {repr(e)}", file=sys.stderr, flush=True)
        emit('error', {'message': 'Failed to send message'})

@app.get("/api/health")
def health():
    return {"ok": True, "time": datetime.datetime.utcnow().isoformat()}

# ============ JWT & SESSION ENDPOINTS ============

@app.post("/api/auth/refresh")
def refresh_token():
    """Refresh JWT access token using refresh token"""
    b = request.get_json(force=True) or {}
    refresh_token = b.get("refresh_token")
    
    if not refresh_token:
        return jsonify({"ok": False, "msg": "Refresh token is required"}), 400
    
    payload = verify_jwt_token(refresh_token)
    if not payload or payload.get('type') != 'refresh':
        return jsonify({"ok": False, "msg": "Invalid refresh token"}), 401
    
    user_id = payload['user_id']
    
    try:
        with engine.begin() as conn:
            # Get user info
            row = conn.execute(text("""
                SELECT u.id, u.email, u.user_type, p.first_name, p.last_name
                FROM users_login u 
                LEFT JOIN immigrant_profile p ON p.user_id = u.id
                WHERE u.id = :user_id AND u.is_active = TRUE
            """), {"user_id": user_id}).fetchone()
            
            if not row:
                return jsonify({"ok": False, "msg": "User not found or inactive"}), 404
            
            # Generate new access token
            access_token = generate_jwt_token(row.id, row.user_type, row.email)
            
            return jsonify({
                "ok": True,
                "tokens": {
                    "access_token": access_token,
                    "expires_in": 86400  # 24 hours in seconds
                }
            }), 200
            
    except Exception as e:
        print("!! /api/auth/refresh error:", repr(e), file=sys.stderr, flush=True)
        return jsonify({"ok": False, "msg": "Token refresh failed", "error": str(e)}), 500

@app.post("/api/auth/logout")
@jwt_required
def logout():
    """Logout user and invalidate session"""
    try:
        # Get session ID from request
        session_id = request.headers.get('X-Session-ID')
        if session_id:
            destroy_session(session_id)
        
        # Log logout event
        log_security_event(
            'LOGOUT',
            f"User logged out: {g.current_user['email']}",
            user_id=g.current_user['user_id'],
            severity='INFO'
        )
        
        return jsonify({"ok": True, "msg": "Logged out successfully"}), 200
        
    except Exception as e:
        print("!! /api/auth/logout error:", repr(e), file=sys.stderr, flush=True)
        return jsonify({"ok": False, "msg": "Logout failed", "error": str(e)}), 500

# ============ SECURITY MONITORING ENDPOINTS ============

@app.get("/api/security/metrics")
@jwt_required
def get_security_metrics_endpoint():
    """Get security metrics (admin only)"""
    # Check if user is admin (you can implement admin role checking)
    if g.current_user['user_type'] not in ['ServiceProvider', 'Admin']:
        return jsonify({"ok": False, "msg": "Access denied"}), 403
    
    try:
        metrics = get_security_metrics()
        return jsonify({"ok": True, "metrics": metrics}), 200
    except Exception as e:
        print("!! /api/security/metrics error:", repr(e), file=sys.stderr, flush=True)
        return jsonify({"ok": False, "msg": "Failed to get metrics", "error": str(e)}), 500

@app.get("/api/security/sessions")
@jwt_required
def get_active_sessions():
    """Get active sessions count"""
    try:
        count = get_active_sessions_count()
        return jsonify({"ok": True, "active_sessions": count}), 200
    except Exception as e:
        print("!! /api/security/sessions error:", repr(e), file=sys.stderr, flush=True)
        return jsonify({"ok": False, "msg": "Failed to get sessions", "error": str(e)}), 500

@app.post("/api/security/cleanup")
@jwt_required
def cleanup_sessions():
    """Clean up expired sessions (admin only)"""
    if g.current_user['user_type'] not in ['ServiceProvider', 'Admin']:
        return jsonify({"ok": False, "msg": "Access denied"}), 403
    
    try:
        cleanup_expired_sessions()
        return jsonify({"ok": True, "msg": "Session cleanup completed"}), 200
    except Exception as e:
        print("!! /api/security/cleanup error:", repr(e), file=sys.stderr, flush=True)
        return jsonify({"ok": False, "msg": "Cleanup failed", "error": str(e)}), 500

@app.post("/api/register")
def register():
    b = request.get_json(force=True) or {}
    email = (b.get("email") or "").strip().lower()
    full_name = (b.get("full_name") or "").strip()
    password = b.get("password") or ""
    user_type = b.get("user_type", "Immigrant")  # Default to Immigrant, can be "ServiceProvider"
    
    # Input validation
    if not email or not password:
        log_security_event("REGISTRATION_FAILURE", "Missing email or password")
        return jsonify({"ok": False, "msg": "email and password required"}), 400
    
    # Validate email format
    if not validate_email(email):
        log_security_event("REGISTRATION_FAILURE", f"Invalid email format: {email}")
        return jsonify({"ok": False, "msg": "Invalid email format"}), 400
    
    # Validate password strength
    is_valid_password, password_msg = validate_password_strength(password)
    if not is_valid_password:
        log_security_event("REGISTRATION_FAILURE", f"Weak password attempt: {password_msg}")
        return jsonify({"ok": False, "msg": password_msg}), 400
    
    # Validate full name
    if not full_name:
        log_security_event("REGISTRATION_FAILURE", "Missing full name")
        return jsonify({"ok": False, "msg": "Full name is required"}), 400
    
    # Sanitize inputs
    email = sanitize_input(email, max_length=255)
    full_name = sanitize_input(full_name, max_length=255)
    user_type = sanitize_input(user_type, max_length=50)

    parts = full_name.split()
    first = parts[0] if parts else ""
    last = " ".join(parts[1:]) if len(parts) > 1 else ""

    user_id = str(uuid.uuid4())
    pw_hash = hash_password(password)

    try:
        with engine.begin() as conn:
            conn.execute(text("""
              INSERT INTO users_login (id, email, password_hash, user_type, created_date)
              VALUES (:id,:email,:hash,:user_type, NOW())
            """), {"id": user_id, "email": email, "hash": pw_hash, "user_type": user_type})

            # Only create immigrant profile for Immigrant users
            if user_type == "Immigrant":
                conn.execute(text("""
                  INSERT INTO immigrant_profile (id, user_id, first_name, last_name, email, created_date)
                  VALUES (:pid,:uid,:fn,:ln,:email, NOW())
                """), {"pid": str(uuid.uuid4()), "uid": user_id, "fn": first, "ln": last, "email": email})

            conn.execute(text("""
              INSERT INTO audit_log (action_type, description, created_by)
              VALUES ('SIGNUP','User created account', :uid)
            """), {"uid": user_id})

        # Create email verification token and send verification email
        verification_token = create_verification_token(user_id)
        if verification_token:
            send_verification_email(email, verification_token, full_name)
            print(f"Verification token created for user {email}: {verification_token}")

        return jsonify({
            "ok": True, 
            "user": {"id": user_id, "email": email, "full_name": full_name, "user_type": user_type},
            "message": "Account created successfully. Please check your email to verify your account before logging in."
        }), 201
    except Exception as e:
        # log full error to server console
        print("!! /api/register error:", repr(e), file=sys.stderr, flush=True)
        return jsonify({"ok": False, "msg": "could not create user", "error": str(e)}), 400

@app.post("/api/login")
@rate_limit(max_requests=10, window_seconds=300)  # 10 login attempts per 5 minutes
def login():
    b = request.get_json(force=True) or {}
    email = (b.get("email") or "").strip().lower()
    password = b.get("password") or ""
    expected_user_type = b.get("user_type", "Immigrant")  # Default to Immigrant for client login
    
    if not email or not password:
        log_security_event("LOGIN_FAILURE", "Missing email or password")
        return jsonify({"ok": False, "msg": "email and password required"}), 400
    
    # Validate email format
    if not validate_email(email):
        log_security_event("LOGIN_FAILURE", f"Invalid email format: {email}")
        return jsonify({"ok": False, "msg": "Invalid email format"}), 400
    
    # Sanitize inputs
    email = sanitize_input(email, max_length=255)
    
    try:
        with engine.begin() as conn:
            # Get user with password hash
            row = conn.execute(text("""
                SELECT u.id, u.email, u.password_hash, u.is_active, u.is_locked, u.user_type, u.email_verified,
                       p.first_name, p.last_name, u.created_date AS created_at
                FROM users_login u 
                LEFT JOIN immigrant_profile p ON p.user_id = u.id
                WHERE u.email = :email
            """), {"email": email}).fetchone()
            
            if not row:
                # Log failed attempt
                conn.execute(text("""
                    INSERT INTO audit_log (action_type, description, created_at)
                    VALUES ('LOGIN_FAILURE', 'User not found: ' || :email, NOW())
                """), {"email": email})
                return jsonify({"ok": False, "msg": "Invalid email or password"}), 401
            
            # Check if account is locked or inactive
            if row.is_locked:
                return jsonify({"ok": False, "msg": "Account is locked. Please contact support."}), 401
            
            if not row.is_active:
                return jsonify({"ok": False, "msg": "Account is inactive. Please contact support."}), 401
            
            # Check if email is verified
            if not row.email_verified:
                return jsonify({"ok": False, "msg": "Please verify your email address before logging in. Check your email for the verification link."}), 401
            
            # Check user type validation
            if expected_user_type == "ServiceProvider" and row.user_type != "ServiceProvider":
                log_security_event("LOGIN_FAILURE", f"Service provider login attempt with client account: {email}")
                return jsonify({"ok": False, "msg": "This account is not registered as a service provider. Please use the client login."}), 401
            elif expected_user_type == "Immigrant" and row.user_type == "ServiceProvider":
                log_security_event("LOGIN_FAILURE", f"Client login attempt with service provider account: {email}")
                return jsonify({"ok": False, "msg": "This account is registered as a service provider. Please use the service provider login."}), 401
            
            # Verify password
            if not verify_password(password, row.password_hash):
                # Log failed attempt and increment login attempts
                conn.execute(text("""
                    UPDATE users_login 
                    SET login_attempts = login_attempts + 1, 
                        attempt_time = NOW()
                    WHERE id = :id
                """), {"id": row.id})
                
                conn.execute(text("""
                    INSERT INTO audit_log (action_type, description, created_by, created_at)
                    VALUES ('LOGIN_FAILURE', 'Invalid password attempt', :uid, NOW())
                """), {"uid": row.id})
                
                return jsonify({"ok": False, "msg": "Invalid email or password"}), 401
            
            # Successful login - reset attempts and update last login
            conn.execute(text("""
                UPDATE users_login 
                SET login_attempts = 0, 
                    last_login = NOW(),
                    login_status = 'SUCCESS'
                WHERE id = :id
            """), {"id": row.id})
            
            # Log successful login
            conn.execute(text("""
                INSERT INTO audit_log (action_type, description, created_by, created_at)
                VALUES ('LOGIN_SUCCESS', 'User logged in successfully', :uid, NOW())
            """), {"uid": row.id})
            
            # Generate JWT tokens
            access_token = generate_jwt_token(row.id, row.user_type, row.email)
            refresh_token = generate_refresh_token(row.id)
            
            # Create session
            session_id = create_session(row.id, row.user_type, row.email)
            
            return jsonify({
                "ok": True, 
                "user": {
                    "id": row.id,
                    "email": row.email,
                    "full_name": " ".join([x for x in [row.first_name, row.last_name] if x]),
                    "user_type": row.user_type,
                    "created_at": row.created_at.isoformat() if row.created_at else None
                },
                "tokens": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_in": 86400  # 24 hours in seconds
                },
                "session_id": session_id
            }), 200
            
    except Exception as e:
        print("!! /api/login error:", repr(e), file=sys.stderr, flush=True)
        return jsonify({"ok": False, "msg": "Login failed", "error": str(e)}), 500

@app.get("/api/users/<user_id>")
def get_user(user_id):
    with engine.begin() as conn:
        row = conn.execute(text("""
            SELECT u.id, u.email, p.first_name, p.last_name, u.created_date AS created_at
            FROM users_login u LEFT JOIN immigrant_profile p ON p.user_id = u.id
            WHERE u.id = :id
        """), {"id": user_id}).fetchone()
    if not row:
        return jsonify({"ok": False, "msg": "not found"}), 404
    return {
        "ok": True,
        "user": {
            "id": row.id,
            "email": row.email,
            "full_name": " ".join([x for x in [row.first_name, row.last_name] if x]),
            "created_at": row.created_at.isoformat() if row.created_at else None
        }
    }

@app.get("/api/users/<user_id>/profile")
def get_user_profile(user_id):
    with engine.begin() as conn:
        row = conn.execute(text("""
            SELECT u.id, u.email, u.created_date AS created_at,
                   p.first_name, p.last_name, p.phone, p.age, p.country_residence,
                   p.desired_destination, p.marital_status, p.family_members,
                   p.referral_source, p.about, p.address
            FROM users_login u 
            LEFT JOIN immigrant_profile p ON p.user_id = u.id
            WHERE u.id = :id
        """), {"id": user_id}).fetchone()
    if not row:
        return jsonify({"ok": False, "msg": "not found"}), 404
    return {
        "ok": True,
        "profile": {
            "id": row.id,
            "email": row.email,
            "first_name": row.first_name,
            "last_name": row.last_name,
            "phone": row.phone,
            "age": row.age,
            "country_residence": row.country_residence,
            "desired_destination": row.desired_destination,
            "marital_status": row.marital_status,
            "family_members": row.family_members,
            "referral_source": row.referral_source,
            "about": row.about,
            "address": row.address,
            "created_at": row.created_at.isoformat() if row.created_at else None
        }
    }

@app.get("/api/service-providers")
def get_service_providers():
    service_type = request.args.get('service_type')
    with engine.begin() as conn:
        query = """
            SELECT id, name, email, phone, address, service_type, description, 
                   website, rating, total_reviews, created_date
            FROM service_providers 
            WHERE is_active = true
        """
        params = {}
        if service_type:
            query += " AND service_type = :service_type"
            params["service_type"] = service_type
        
        query += " ORDER BY rating DESC, name ASC"
        
        rows = conn.execute(text(query), params).fetchall()
    
    providers = []
    for row in rows:
        providers.append({
            "id": row.id,
            "name": row.name,
            "email": row.email,
            "phone": row.phone,
            "address": row.address,
            "service_type": row.service_type,
            "description": row.description,
            "website": row.website,
            "rating": float(row.rating) if row.rating else 0.0,
            "total_reviews": row.total_reviews,
            "created_date": row.created_date.isoformat() if row.created_date else None
        })
    
    return {"ok": True, "providers": providers}

@app.post("/api/service-requests")
@jwt_required
@rate_limit(max_requests=20, window_seconds=300)  # 20 requests per 5 minutes
def create_service_request():
    b = request.get_json(force=True) or {}
    user_id = b.get("user_id")
    provider_id = b.get("provider_id")
    service_type = b.get("service_type")
    title = b.get("title")
    description = b.get("description", "")
    priority = b.get("priority", "MEDIUM")
    
    if not all([user_id, provider_id, service_type, title]):
        log_security_event("SERVICE_REQUEST_FAILURE", "Missing required fields")
        return jsonify({"ok": False, "msg": "user_id, provider_id, service_type, and title are required"}), 400
    
    # Validate service type
    is_valid_service, service_msg = validate_service_type(service_type)
    if not is_valid_service:
        log_security_event("SERVICE_REQUEST_FAILURE", f"Invalid service type: {service_type}")
        return jsonify({"ok": False, "msg": service_msg}), 400
    
    # Validate priority
    is_valid_priority, priority_msg = validate_priority(priority)
    if not is_valid_priority:
        log_security_event("SERVICE_REQUEST_FAILURE", f"Invalid priority: {priority}")
        return jsonify({"ok": False, "msg": priority_msg}), 400
    
    # Sanitize inputs
    title = sanitize_input(title, max_length=255)
    description = sanitize_input(description, max_length=2000)
    service_type = sanitize_input(service_type, max_length=100)
    priority = sanitize_input(priority, max_length=20)
    
    request_id = str(uuid.uuid4())
    
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO service_requests (id, user_id, provider_id, service_type, title, description, priority, requested_date)
                VALUES (:id, :user_id, :provider_id, :service_type, :title, :description, :priority, NOW())
            """), {
                "id": request_id,
                "user_id": user_id,
                "provider_id": provider_id,
                "service_type": service_type,
                "title": title,
                "description": description,
                "priority": priority
            })
            
            conn.execute(text("""
                INSERT INTO audit_log (action_type, description, created_by, created_at)
                VALUES ('SERVICE_REQUEST', 'Service request created: ' || :title, :uid, NOW())
            """), {"title": title, "uid": user_id})
        
        return jsonify({"ok": True, "request_id": request_id}), 201
    except Exception as e:
        print("!! /api/service-requests error:", repr(e), file=sys.stderr, flush=True)
        return jsonify({"ok": False, "msg": "Could not create service request", "error": str(e)}), 400

@app.get("/api/users/<user_id>/service-requests")
@jwt_required
def get_user_service_requests(user_id):
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT sr.id, sr.service_type, sr.title, sr.description, sr.status, sr.priority,
                   sr.requested_date, sr.accepted_date, sr.completed_date, sr.notes,
                   sp.name as provider_name, sp.email as provider_email, sp.phone as provider_phone
            FROM service_requests sr
            JOIN service_providers sp ON sp.id = sr.provider_id
            WHERE sr.user_id = :user_id AND sr.status != 'CONFIRMED'
            ORDER BY sr.requested_date DESC
        """), {"user_id": user_id}).fetchall()
    
    requests = []
    for row in rows:
        requests.append({
            "id": row.id,
            "service_type": row.service_type,
            "title": row.title,
            "description": row.description,
            "status": row.status,
            "priority": row.priority,
            "requested_date": row.requested_date.isoformat() if row.requested_date else None,
            "accepted_date": row.accepted_date.isoformat() if row.accepted_date else None,
            "completed_date": row.completed_date.isoformat() if row.completed_date else None,
            "notes": row.notes,
            "provider": {
                "name": row.provider_name,
                "email": row.provider_email,
                "phone": row.provider_phone
            }
        })
    
    return {"ok": True, "requests": requests}

# ============ SERVICE PROVIDER ENDPOINTS ============

@app.post("/api/service-providers/register")
def register_service_provider():
    b = request.get_json(force=True) or {}
    email = (b.get("email") or "").strip().lower()
    first_name = (b.get("first_name") or "").strip()
    last_name = (b.get("last_name") or "").strip()
    name = (b.get("name") or "").strip()
    password = b.get("password") or ""
    phone = b.get("phone", "")
    address = b.get("address", "")
    service_type = b.get("service_type", "")
    description = b.get("description", "")
    website = b.get("website", "")
    
    # Input validation
    if not all([email, first_name, last_name, name, password, service_type]):
        log_security_event("PROVIDER_REGISTRATION_FAILURE", "Missing required fields")
        return jsonify({"ok": False, "msg": "email, first_name, last_name, name, password, and service_type are required"}), 400
    
    # Validate email format
    if not validate_email(email):
        log_security_event("PROVIDER_REGISTRATION_FAILURE", f"Invalid email format: {email}")
        return jsonify({"ok": False, "msg": "Invalid email format"}), 400
    
    # Validate password strength
    is_valid_password, password_msg = validate_password_strength(password)
    if not is_valid_password:
        log_security_event("PROVIDER_REGISTRATION_FAILURE", f"Weak password attempt: {password_msg}")
        return jsonify({"ok": False, "msg": password_msg}), 400
    
    # Validate names
    is_valid_first, first_msg = validate_name(first_name, "First name")
    if not is_valid_first:
        return jsonify({"ok": False, "msg": first_msg}), 400
    
    is_valid_last, last_msg = validate_name(last_name, "Last name")
    if not is_valid_last:
        return jsonify({"ok": False, "msg": last_msg}), 400
    
    is_valid_name, name_msg = validate_name(name, "Business name")
    if not is_valid_name:
        return jsonify({"ok": False, "msg": name_msg}), 400
    
    # Validate service type
    is_valid_service, service_msg = validate_service_type(service_type)
    if not is_valid_service:
        return jsonify({"ok": False, "msg": service_msg}), 400
    
    # Validate phone (optional)
    if phone:
        is_valid_phone, phone_msg = validate_phone(phone)
        if not is_valid_phone:
            return jsonify({"ok": False, "msg": phone_msg}), 400
    
    # Sanitize inputs
    email = sanitize_input(email, max_length=255)
    first_name = sanitize_input(first_name, max_length=100)
    last_name = sanitize_input(last_name, max_length=100)
    name = sanitize_input(name, max_length=255)
    phone = sanitize_input(phone, max_length=50)
    address = sanitize_input(address, max_length=500)
    service_type = sanitize_input(service_type, max_length=100)
    description = sanitize_input(description, max_length=2000)
    website = sanitize_input(website, max_length=255)
    
    user_id = str(uuid.uuid4())
    provider_id = str(uuid.uuid4())
    pw_hash = hash_password(password)
    
    try:
        with engine.begin() as conn:
            # Create user account
            conn.execute(text("""
                INSERT INTO users_login (id, email, password_hash, user_type, created_date)
                VALUES (:id, :email, :hash, 'ServiceProvider', NOW())
            """), {"id": user_id, "email": email, "hash": pw_hash})
            
            # Create immigrant profile for the service provider
            conn.execute(text("""
                INSERT INTO immigrant_profile (id, user_id, first_name, last_name, email, created_date)
                VALUES (:pid, :uid, :fn, :ln, :email, NOW())
            """), {"pid": str(uuid.uuid4()), "uid": user_id, "fn": first_name, "ln": last_name, "email": email})
            
            # Create service provider profile
            conn.execute(text("""
                INSERT INTO service_providers (id, user_id, name, email, phone, address, 
                                             service_type, description, website, created_date)
                VALUES (:id, :user_id, :name, :email, :phone, :address, :service_type, 
                       :description, :website, NOW())
            """), {
                "id": provider_id,
                "user_id": user_id,
                "name": name,
                "email": email,
                "phone": phone,
                "address": address,
                "service_type": service_type,
                "description": description,
                "website": website
            })
            
            conn.execute(text("""
                INSERT INTO audit_log (action_type, description, created_by, created_at)
                VALUES ('SERVICE_PROVIDER_SIGNUP', 'Service provider registered: ' || :name, :uid, NOW())
            """), {"name": name, "uid": user_id})
        
        return jsonify({
            "ok": True, 
            "provider": {
                "id": provider_id,
                "user_id": user_id,
                "name": name,
                "email": email,
                "service_type": service_type
            }
        }), 201
    except Exception as e:
        print("!! /api/service-providers/register error:", repr(e), file=sys.stderr, flush=True)
        return jsonify({"ok": False, "msg": "Could not create service provider", "error": str(e)}), 400

@app.get("/api/users/<user_id>/provider-profile")
def get_user_provider_profile(user_id):
    with engine.begin() as conn:
        row = conn.execute(text("""
            SELECT sp.id as provider_id, sp.name, sp.email, sp.service_type, sp.description,
                   u.email as user_email, p.first_name, p.last_name
            FROM service_providers sp
            JOIN users_login u ON sp.user_id = u.id
            LEFT JOIN immigrant_profile p ON p.user_id = u.id
            WHERE sp.user_id = :user_id
        """), {"user_id": user_id}).fetchone()
    
    if not row:
        return jsonify({"ok": False, "msg": "Provider profile not found"}), 404
    
    return {
        "ok": True,
        "provider": {
            "id": row.provider_id,
            "name": row.name,
            "email": row.email,
            "service_type": row.service_type,
            "description": row.description,
            "first_name": row.first_name,
            "last_name": row.last_name
        }
    }

@app.get("/api/service-providers/<provider_id>/requests")
def get_provider_service_requests(provider_id):
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT sr.id, sr.service_type, sr.title, sr.description, sr.status, sr.priority,
                   sr.requested_date, sr.accepted_date, sr.completed_date, sr.notes,
                   u.email as client_email, p.first_name as client_first_name, 
                   p.last_name as client_last_name
            FROM service_requests sr
            JOIN users_login u ON u.id = sr.user_id
            LEFT JOIN immigrant_profile p ON p.user_id = u.id
            WHERE sr.provider_id = :provider_id AND sr.status != 'CONFIRMED'
            ORDER BY sr.requested_date DESC
        """), {"provider_id": provider_id}).fetchall()
    
    requests = []
    for row in rows:
        requests.append({
            "id": row.id,
            "service_type": row.service_type,
            "title": row.title,
            "description": row.description,
            "status": row.status,
            "priority": row.priority,
            "requested_date": row.requested_date.isoformat() if row.requested_date else None,
            "accepted_date": row.accepted_date.isoformat() if row.accepted_date else None,
            "completed_date": row.completed_date.isoformat() if row.completed_date else None,
            "notes": row.notes,
            "client": {
                "email": row.client_email,
                "name": " ".join([x for x in [row.client_first_name, row.client_last_name] if x]) or "Unknown"
            }
        })
    
    return {"ok": True, "requests": requests}

@app.post("/api/service-requests/<request_id>/accept")
def accept_service_request(request_id):
    b = request.get_json(force=True) or {}
    provider_id = b.get("provider_id")
    notes = b.get("notes", "")
    
    if not provider_id:
        return jsonify({"ok": False, "msg": "provider_id is required"}), 400
    
    try:
        with engine.begin() as conn:
            # Update request status
            result = conn.execute(text("""
                UPDATE service_requests 
                SET status = 'ACCEPTED', accepted_date = NOW(), notes = :notes
                WHERE id = :request_id AND provider_id = :provider_id
            """), {"request_id": request_id, "provider_id": provider_id, "notes": notes})
            
            if result.rowcount == 0:
                return jsonify({"ok": False, "msg": "Request not found or not authorized"}), 404
            
            # Create conversation for messaging
            conversation_id = str(uuid.uuid4())
            conn.execute(text("""
                INSERT INTO conversations (id, service_request_id, user_id, provider_id, created_date)
                SELECT :conv_id, :req_id, sr.user_id, sr.provider_id, NOW()
                FROM service_requests sr
                WHERE sr.id = :req_id
            """), {"conv_id": conversation_id, "req_id": request_id})
            
            conn.execute(text("""
                INSERT INTO audit_log (action_type, description, created_by, created_at)
                VALUES ('SERVICE_REQUEST_ACCEPTED', 'Service request accepted: ' || :req_id, :pid, NOW())
            """), {"req_id": request_id, "pid": provider_id})
        
        return jsonify({"ok": True, "conversation_id": conversation_id}), 200
    except Exception as e:
        print("!! /api/service-requests/accept error:", repr(e), file=sys.stderr, flush=True)
        return jsonify({"ok": False, "msg": "Could not accept request", "error": str(e)}), 400

@app.put("/api/service-requests/<request_id>/complete")
def complete_service_request(request_id):
    b = request.get_json(force=True) or {}
    provider_id = b.get("provider_id")
    completion_notes = b.get("completion_notes", "")
    
    if not provider_id:
        return jsonify({"ok": False, "msg": "provider_id is required"}), 400
    
    try:
        with engine.begin() as conn:
            # Verify the request exists and belongs to this provider
            request_row = conn.execute(text("""
                SELECT sr.id, sr.provider_id, sr.status, sr.user_id
                FROM service_requests sr
                WHERE sr.id = :req_id AND sr.provider_id = :provider_id
            """), {"req_id": request_id, "provider_id": provider_id}).fetchone()
            
            if not request_row:
                return jsonify({"ok": False, "msg": "Service request not found or unauthorized"}), 404
            
            if request_row.status != 'ACCEPTED':
                return jsonify({"ok": False, "msg": "Only accepted requests can be completed"}), 400
            
            # Update the service request status to COMPLETED
            conn.execute(text("""
                UPDATE service_requests 
                SET status = 'COMPLETED', 
                    completed_date = NOW(),
                    notes = CASE 
                        WHEN :notes != '' THEN COALESCE(notes, '') || '\n\nCompletion Notes: ' || :notes
                        ELSE notes
                    END
                WHERE id = :req_id
            """), {"req_id": request_id, "notes": completion_notes})
            
            # Log the completion
            conn.execute(text("""
                INSERT INTO audit_log (action_type, description, created_by, created_at)
                VALUES ('SERVICE_COMPLETED', 'Service request completed: ' || :req_id, :pid, NOW())
            """), {"req_id": request_id, "pid": provider_id})
        
        return jsonify({"ok": True, "msg": "Service marked as completed successfully"}), 200
    except Exception as e:
        print("!! /api/service-requests/complete error:", repr(e), file=sys.stderr, flush=True)
        return jsonify({"ok": False, "msg": "Could not complete service", "error": str(e)}), 400

@app.put("/api/service-requests/<request_id>/confirm")
def confirm_service_completion(request_id):
    b = request.get_json(force=True) or {}
    user_id = b.get("user_id")
    rating = b.get("rating")
    
    if not user_id or not rating:
        return jsonify({"ok": False, "msg": "user_id and rating are required"}), 400
    
    if rating < 1 or rating > 5:
        return jsonify({"ok": False, "msg": "Rating must be between 1 and 5"}), 400
    
    try:
        with engine.begin() as conn:
            # Verify the request exists and belongs to this user
            request_row = conn.execute(text("""
                SELECT sr.id, sr.user_id, sr.status, sr.provider_id
                FROM service_requests sr
                WHERE sr.id = :req_id AND sr.user_id = :user_id
            """), {"req_id": request_id, "user_id": user_id}).fetchone()
            
            if not request_row:
                return jsonify({"ok": False, "msg": "Service request not found or unauthorized"}), 404
            
            if request_row.status != 'COMPLETED':
                return jsonify({"ok": False, "msg": "Only completed requests can be confirmed"}), 400
            
            # Update the service request status to CONFIRMED and add rating
            conn.execute(text("""
                UPDATE service_requests 
                SET status = 'CONFIRMED',
                    client_rating = :rating,
                    confirmed_date = NOW()
                WHERE id = :req_id
            """), {"req_id": request_id, "rating": rating})
            
            # Update provider's rating (calculate new average)
            conn.execute(text("""
                UPDATE service_providers 
                SET total_reviews = total_reviews + 1,
                    rating = (
                        SELECT AVG(CAST(client_rating AS DECIMAL))
                        FROM service_requests 
                        WHERE provider_id = :provider_id 
                        AND client_rating IS NOT NULL
                    )
                WHERE id = :provider_id
            """), {"provider_id": request_row.provider_id})
            
            # Log the confirmation
            conn.execute(text("""
                INSERT INTO audit_log (action_type, description, created_by, created_at)
                VALUES ('SERVICE_CONFIRMED', 'Service request confirmed with rating: ' || :rating || ' for request: ' || :req_id, :uid, NOW())
            """), {"req_id": request_id, "rating": rating, "uid": user_id})
        
        return jsonify({"ok": True, "msg": "Service confirmed and rating recorded successfully"}), 200
    except Exception as e:
        print("!! /api/service-requests/confirm error:", repr(e), file=sys.stderr, flush=True)
        return jsonify({"ok": False, "msg": "Could not confirm service", "error": str(e)}), 400

# ============ MESSAGING ENDPOINTS ============

@app.get("/api/service-requests/<request_id>/conversation")
def get_request_conversation(request_id):
    with engine.begin() as conn:
        row = conn.execute(text("""
            SELECT c.id as conversation_id, c.status, c.created_date, c.updated_date
            FROM conversations c
            WHERE c.service_request_id = :request_id
        """), {"request_id": request_id}).fetchone()
    
    if not row:
        return jsonify({"ok": False, "msg": "Conversation not found"}), 404
    
    return {
        "ok": True,
        "conversation": {
            "id": row.conversation_id,
            "status": row.status,
            "created_date": row.created_date.isoformat() if row.created_date else None,
            "updated_date": row.updated_date.isoformat() if row.updated_date else None
        }
    }

@app.get("/api/conversations/<conversation_id>/messages")
def get_conversation_messages(conversation_id):
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT id, sender_id, sender_type, message_text, is_read, created_date
            FROM messages
            WHERE conversation_id = :conversation_id
            ORDER BY created_date ASC
        """), {"conversation_id": conversation_id}).fetchall()
    
    messages = []
    for row in rows:
        messages.append({
            "id": row.id,
            "sender_id": row.sender_id,
            "sender_type": row.sender_type,
            "message_text": row.message_text,
            "is_read": row.is_read,
            "created_date": row.created_date.isoformat() if row.created_date else None
        })
    
    return {"ok": True, "messages": messages}

@app.post("/api/conversations/<conversation_id>/messages")
def send_message(conversation_id):
    b = request.get_json(force=True) or {}
    sender_id = b.get("sender_id")
    sender_type = b.get("sender_type")  # 'CLIENT' or 'PROVIDER'
    message_text = b.get("message_text", "").strip()
    
    if not all([sender_id, sender_type, message_text]):
        return jsonify({"ok": False, "msg": "sender_id, sender_type, and message_text are required"}), 400
    
    if sender_type not in ['CLIENT', 'PROVIDER']:
        return jsonify({"ok": False, "msg": "sender_type must be 'CLIENT' or 'PROVIDER'"}), 400
    
    message_id = str(uuid.uuid4())
    
    try:
        with engine.begin() as conn:
            # Verify conversation exists and sender is authorized
            conv = conn.execute(text("""
                SELECT user_id, provider_id FROM conversations WHERE id = :conv_id
            """), {"conv_id": conversation_id}).fetchone()
            
            if not conv:
                return jsonify({"ok": False, "msg": "Conversation not found"}), 404
            
            # Check authorization
            if sender_type == 'CLIENT' and conv.user_id != sender_id:
                return jsonify({"ok": False, "msg": "Unauthorized"}), 403
            elif sender_type == 'PROVIDER':
                # For providers, we need to check if the sender_id matches the user_id 
                # that corresponds to the provider_id in the conversation
                provider_user = conn.execute(text("""
                    SELECT user_id FROM service_providers WHERE id = :provider_id
                """), {"provider_id": conv.provider_id}).fetchone()
                
                if not provider_user or provider_user.user_id != sender_id:
                    return jsonify({"ok": False, "msg": "Unauthorized"}), 403
            
            # Insert message
            conn.execute(text("""
                INSERT INTO messages (id, conversation_id, sender_id, sender_type, message_text, created_date)
                VALUES (:id, :conversation_id, :sender_id, :sender_type, :message_text, NOW())
            """), {
                "id": message_id,
                "conversation_id": conversation_id,
                "sender_id": sender_id,
                "sender_type": sender_type,
                "message_text": message_text
            })
            
            conn.execute(text("""
                INSERT INTO audit_log (action_type, description, created_by, created_at)
                VALUES ('MESSAGE_SENT', 'Message sent in conversation: ' || :conv_id, :sender_id, NOW())
            """), {"conv_id": conversation_id, "sender_id": sender_id})
        
        return jsonify({"ok": True, "message_id": message_id}), 201
    except Exception as e:
        print("!! /api/conversations/messages error:", repr(e), file=sys.stderr, flush=True)
        return jsonify({"ok": False, "msg": "Could not send message", "error": str(e)}), 400

@app.get("/api/users/<user_id>/conversations")
def get_user_conversations(user_id):
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT c.id, c.service_request_id, c.status, c.created_date, c.updated_date,
                   sr.title as request_title, sr.status as request_status,
                   sp.name as provider_name, sp.service_type
            FROM conversations c
            JOIN service_requests sr ON sr.id = c.service_request_id
            JOIN service_providers sp ON sp.id = c.provider_id
            WHERE c.user_id = :user_id
            ORDER BY c.updated_date DESC
        """), {"user_id": user_id}).fetchall()
    
    conversations = []
    for row in rows:
        conversations.append({
            "id": row.id,
            "service_request_id": row.service_request_id,
            "status": row.status,
            "created_date": row.created_date.isoformat() if row.created_date else None,
            "updated_date": row.updated_date.isoformat() if row.updated_date else None,
            "request_title": row.request_title,
            "request_status": row.request_status,
            "provider_name": row.provider_name,
            "service_type": row.service_type
        })
    
    return {"ok": True, "conversations": conversations}

@app.put("/api/conversations/<conversation_id>/messages/<message_id>/read")
def mark_message_read(conversation_id, message_id):
    try:
        with engine.begin() as conn:
            result = conn.execute(text("""
                UPDATE messages 
                SET is_read = true 
                WHERE id = :message_id AND conversation_id = :conversation_id
            """), {"message_id": message_id, "conversation_id": conversation_id})
            
            if result.rowcount == 0:
                return jsonify({"ok": False, "msg": "Message not found"}), 404
            
            return jsonify({"ok": True}), 200
    except Exception as e:
        print("!! /api/conversations/messages/read error:", repr(e), file=sys.stderr, flush=True)
        return jsonify({"ok": False, "msg": "Could not mark message as read", "error": str(e)}), 400

@app.get("/api/service-providers/<provider_id>/conversations")
def get_provider_conversations(provider_id):
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT c.id, c.service_request_id, c.status, c.created_date, c.updated_date,
                   sr.title as request_title, sr.status as request_status,
                   u.email as client_email, p.first_name as client_first_name, 
                   p.last_name as client_last_name
            FROM conversations c
            JOIN service_requests sr ON sr.id = c.service_request_id
            JOIN users_login u ON u.id = c.user_id
            LEFT JOIN immigrant_profile p ON p.user_id = u.id
            WHERE c.provider_id = :provider_id
            ORDER BY c.updated_date DESC
        """), {"provider_id": provider_id}).fetchall()
    
    conversations = []
    for row in rows:
        conversations.append({
            "id": row.id,
            "service_request_id": row.service_request_id,
            "status": row.status,
            "created_date": row.created_date.isoformat() if row.created_date else None,
            "updated_date": row.updated_date.isoformat() if row.updated_date else None,
            "request_title": row.request_title,
            "request_status": row.request_status,
            "client": {
                "email": row.client_email,
                "name": " ".join([x for x in [row.client_first_name, row.client_last_name] if x]) or "Unknown"
            }
        })
    
    return {"ok": True, "conversations": conversations}

# ============ EMAIL VERIFICATION ENDPOINTS ============

@app.post("/api/verify-email")
@rate_limit(max_requests=5, window_seconds=300)  # 5 verification attempts per 5 minutes
def verify_email():
    """Verify email address using token"""
    b = request.get_json(force=True) or {}
    token = b.get("token", "").strip()
    
    if not token:
        return jsonify({"ok": False, "msg": "Verification token is required"}), 400
    
    success, message = verify_email_token(token)
    
    if success:
        log_security_event("EMAIL_VERIFIED", f"Email verified successfully")
        return jsonify({"ok": True, "msg": message}), 200
    else:
        log_security_event("EMAIL_VERIFICATION_FAILED", f"Email verification failed: {message}")
        return jsonify({"ok": False, "msg": message}), 400

@app.post("/api/resend-verification")
@rate_limit(max_requests=3, window_seconds=300)  # 3 resend attempts per 5 minutes
def resend_verification():
    """Resend email verification token"""
    b = request.get_json(force=True) or {}
    email = (b.get("email") or "").strip().lower()
    
    if not email:
        return jsonify({"ok": False, "msg": "Email is required"}), 400
    
    if not validate_email(email):
        return jsonify({"ok": False, "msg": "Invalid email format"}), 400
    
    try:
        with engine.begin() as conn:
            # Check if user exists and is not already verified
            user = conn.execute(text("""
                SELECT id, email_verified, user_type
                FROM users_login
                WHERE email = :email
            """), {"email": email}).fetchone()
            
            if not user:
                return jsonify({"ok": False, "msg": "User not found"}), 404
            
            if user.email_verified:
                return jsonify({"ok": False, "msg": "Email is already verified"}), 400
            
            # Create new verification token
            verification_token = create_verification_token(user.id)
            if verification_token:
                send_verification_email(email, verification_token)
                log_security_event("VERIFICATION_RESENT", f"Verification email resent to {email}")
                return jsonify({"ok": True, "msg": "Verification email sent successfully"}), 200
            else:
                return jsonify({"ok": False, "msg": "Failed to create verification token"}), 500
                
    except Exception as e:
        print(f"Error resending verification: {e}")
        return jsonify({"ok": False, "msg": "Error resending verification"}), 500

if __name__ == "__main__":
    print(f">> Starting Flask with SocketIO on 0.0.0.0:{PORT}", flush=True)
    socketio.run(app, port=PORT, debug=True, host="0.0.0.0", allow_unsafe_werkzeug=True)
