"""
Authentication and User Session Management for Medi-Caps Regulations Portal.
Provides password hashing, JWT token generation, pre-seeded demo accounts,
and session validation.
"""
import os
import time
import json
import hashlib
import hmac
from typing import Optional, Dict, Any
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

USERS_DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "corpus", "users_db.json")

def hash_password(password: str, salt: str = "medicaps_salt_2024") -> str:
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

class AuthManager:
    def __init__(self):
        self.users = {}
        self._init_users()

    def _init_users(self):
        if os.path.exists(USERS_DB_FILE):
            try:
                with open(USERS_DB_FILE, "r", encoding="utf-8") as f:
                    self.users = json.load(f)
                    return
            except Exception:
                pass

        # Seed initial demo accounts
        self.users = {
            "student@medicaps.ac.in": {
                "email": "student@medicaps.ac.in",
                "name": "Aarav Sharma",
                "enrollment_no": "EN21CS301045",
                "department": "Computer Science & Engineering",
                "role": "student",
                "password_hash": hash_password("guest123"),
                "created_at": time.time()
            },
            "admin@medicaps.ac.in": {
                "email": "admin@medicaps.ac.in",
                "name": "Dr. Sunita Kulkarni",
                "enrollment_no": "FAC-REG-104",
                "department": "Academic Registrar Office",
                "role": "admin",
                "password_hash": hash_password("admin123"),
                "created_at": time.time()
            }
        }
        self._save_users()

    def _save_users(self):
        try:
            with open(USERS_DB_FILE, "w", encoding="utf-8") as f:
                json.dump(self.users, f, indent=2)
        except Exception:
            pass

    def register(self, email: str, password: str, name: str, enrollment_no: str, department: str = "B.Tech CSE") -> Dict[str, Any]:
        email = email.lower().strip()
        if email in self.users:
            return {"success": False, "error": "User with this email already exists"}

        user = {
            "email": email,
            "name": name.strip(),
            "enrollment_no": enrollment_no.strip(),
            "department": department.strip(),
            "role": "student",
            "password_hash": hash_password(password),
            "created_at": time.time()
        }
        self.users[email] = user
        self._save_users()
        token = self.create_token(email)
        return {
            "success": True,
            "token": token,
            "user": {
                "email": user["email"],
                "name": user["name"],
                "enrollment_no": user["enrollment_no"],
                "department": user["department"],
                "role": user["role"]
            }
        }

    def authenticate(self, email: str, password: str) -> Dict[str, Any]:
        email = email.lower().strip()
        user = self.users.get(email)
        if not user or user["password_hash"] != hash_password(password):
            return {"success": False, "error": "Invalid email or password"}

        token = self.create_token(email)
        return {
            "success": True,
            "token": token,
            "user": {
                "email": user["email"],
                "name": user["name"],
                "enrollment_no": user["enrollment_no"],
                "department": user["department"],
                "role": user["role"]
            }
        }

    def create_token(self, email: str) -> str:
        payload = {
            "email": email,
            "exp": time.time() + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        }
        raw = json.dumps(payload)
        sig = hmac.new(SECRET_KEY.encode('utf-8'), raw.encode('utf-8'), hashlib.sha256).hexdigest()
        import base64
        token_part = base64.b64encode(raw.encode('utf-8')).decode('utf-8')
        return f"{token_part}.{sig}"

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        if not token or "." not in token:
            return None
        try:
            import base64
            parts = token.split(".")
            raw = base64.b64decode(parts[0].encode('utf-8')).decode('utf-8')
            sig = parts[1]
            expected_sig = hmac.new(SECRET_KEY.encode('utf-8'), raw.encode('utf-8'), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig, expected_sig):
                return None
            data = json.loads(raw)
            if data.get("exp", 0) < time.time():
                return None
            email = data.get("email")
            user = self.users.get(email)
            if not user:
                return None
            return {
                "email": user["email"],
                "name": user["name"],
                "enrollment_no": user["enrollment_no"],
                "department": user["department"],
                "role": user["role"]
            }
        except Exception:
            return None
