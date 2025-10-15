# app.py
import os, uuid, datetime, sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from sqlalchemy import create_engine, text
import hashlib
from dotenv import load_dotenv

print(">> Loading .env", flush=True)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
PORT = int(os.getenv("PORT", "5001"))

if not DATABASE_URL:
    print("!! DATABASE_URL is missing in .env", file=sys.stderr, flush=True)
    sys.exit(1)

print(f">> Connecting to DB: {DATABASE_URL}", flush=True)
engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Simple password hashing function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hashlib.sha256(password.encode()).hexdigest() == hashed

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

@app.post("/api/register")
def register():
    b = request.get_json(force=True) or {}
    email = (b.get("email") or "").strip().lower()
    full_name = (b.get("full_name") or "").strip()
    password = b.get("password") or ""
    user_type = b.get("user_type", "Immigrant")  # Default to Immigrant, can be "ServiceProvider"
    
    if not email or not password:
        return jsonify({"ok": False, "msg": "email and password required"}), 400

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

        return jsonify({"ok": True, "user": {"id": user_id, "email": email, "full_name": full_name, "user_type": user_type}}), 201
    except Exception as e:
        # log full error to server console
        print("!! /api/register error:", repr(e), file=sys.stderr, flush=True)
        return jsonify({"ok": False, "msg": "could not create user", "error": str(e)}), 400

@app.post("/api/login")
def login():
    b = request.get_json(force=True) or {}
    email = (b.get("email") or "").strip().lower()
    password = b.get("password") or ""
    
    if not email or not password:
        return jsonify({"ok": False, "msg": "email and password required"}), 400
    
    try:
        with engine.begin() as conn:
            # Get user with password hash
            row = conn.execute(text("""
                SELECT u.id, u.email, u.password_hash, u.is_active, u.is_locked, u.user_type,
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
            
            return jsonify({
                "ok": True, 
                "user": {
                    "id": row.id,
                    "email": row.email,
                    "full_name": " ".join([x for x in [row.first_name, row.last_name] if x]),
                    "user_type": row.user_type,
                    "created_at": row.created_at.isoformat() if row.created_at else None
                }
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
def create_service_request():
    b = request.get_json(force=True) or {}
    user_id = b.get("user_id")
    provider_id = b.get("provider_id")
    service_type = b.get("service_type")
    title = b.get("title")
    description = b.get("description", "")
    priority = b.get("priority", "MEDIUM")
    
    if not all([user_id, provider_id, service_type, title]):
        return jsonify({"ok": False, "msg": "user_id, provider_id, service_type, and title are required"}), 400
    
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
def get_user_service_requests(user_id):
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT sr.id, sr.service_type, sr.title, sr.description, sr.status, sr.priority,
                   sr.requested_date, sr.accepted_date, sr.completed_date, sr.notes,
                   sp.name as provider_name, sp.email as provider_email, sp.phone as provider_phone
            FROM service_requests sr
            JOIN service_providers sp ON sp.id = sr.provider_id
            WHERE sr.user_id = :user_id
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
    name = (b.get("name") or "").strip()
    password = b.get("password") or ""
    phone = b.get("phone", "")
    address = b.get("address", "")
    service_type = b.get("service_type", "")
    description = b.get("description", "")
    website = b.get("website", "")
    
    if not all([email, name, password, service_type]):
        return jsonify({"ok": False, "msg": "email, name, password, and service_type are required"}), 400
    
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
            SELECT sp.id as provider_id, sp.name, sp.email, sp.service_type, sp.description
            FROM service_providers sp
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
            "description": row.description
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
            WHERE sr.provider_id = :provider_id
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

if __name__ == "__main__":
    print(f">> Starting Flask with SocketIO on 0.0.0.0:{PORT}", flush=True)
    socketio.run(app, port=PORT, debug=True, host="0.0.0.0", allow_unsafe_werkzeug=True)
