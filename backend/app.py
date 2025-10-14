# app.py
import os, uuid, datetime, sys
from flask import Flask, request, jsonify
from flask_cors import CORS
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

# Simple password hashing function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hashlib.sha256(password.encode()).hexdigest() == hashed

@app.get("/api/health")
def health():
    return {"ok": True, "time": datetime.datetime.utcnow().isoformat()}

@app.post("/api/register")
def register():
    b = request.get_json(force=True) or {}
    email = (b.get("email") or "").strip().lower()
    full_name = (b.get("full_name") or "").strip()
    password = b.get("password") or ""
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
              VALUES (:id,:email,:hash,'Immigrant', NOW())
            """), {"id": user_id, "email": email, "hash": pw_hash})

            conn.execute(text("""
              INSERT INTO immigrant_profile (id, user_id, first_name, last_name, email, created_date)
              VALUES (:pid,:uid,:fn,:ln,:email, NOW())
            """), {"pid": str(uuid.uuid4()), "uid": user_id, "fn": first, "ln": last, "email": email})

            conn.execute(text("""
              INSERT INTO audit_log (action_type, description, created_by)
              VALUES ('SIGNUP','User created account', :uid)
            """), {"uid": user_id})

        return jsonify({"ok": True, "user": {"id": user_id, "email": email, "full_name": full_name}}), 201
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
                SELECT u.id, u.email, u.password_hash, u.is_active, u.is_locked, 
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

if __name__ == "__main__":
    print(f">> Starting Flask on 0.0.0.0:{PORT}", flush=True)
    app.run(port=PORT, debug=True, host="0.0.0.0")
