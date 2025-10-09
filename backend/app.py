# app.py
import os, uuid, datetime, sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, text
from passlib.hash import bcrypt
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
    pw_hash = bcrypt.hash(password)

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

@app.get("/api/users/<user_id>")
def get_user(user_id):
    with engine.begin() as conn:
        row = conn.execute(text("""
            SELECT u.id, u.email, p.first_name, p.last_name, u.created_date AS created_at
            FROM users_login u LEFT JOIN immigrant_profile p ON p.user_id = u.id
            WHERE u.id = :id
        """), {"id": user_id}).m.fetchone()
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

if __name__ == "__main__":
    print(f">> Starting Flask on 0.0.0.0:{PORT}", flush=True)
    app.run(port=PORT, debug=True, host="0.0.0.0")
