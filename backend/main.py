from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import os

# Simple in-memory database connection
def get_db():
    import psycopg2
    import psycopg2.extras
    return psycopg2.connect(os.getenv("DATABASE_URL", "postgresql://localhost/zero"))

app = FastAPI(title="Zero Trust Security Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth endpoint
@app.post("/auth/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    try:
        db = get_db()
        cursor = db.cursor(cursor_factory=__import__('psycopg2.extras', fromlist=['RealDictCursor']).RealDictCursor)
        
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        
        success = bool(user)
        ip = request.client.host if request.client else "Unknown"
        
        cursor.execute("""
            INSERT INTO login_logs (user_id, login_time, ip_address, success, country, city)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (username, datetime.now(), ip, success, "Unknown", "Unknown"))
        db.commit()
        cursor.close()
        db.close()
        
        if not success:
            return {"status": "FAIL", "message": "Invalid credentials"}
        
        return {
            "status": "SUCCESS",
            "user": username,
            "role": user["role"],
            "location": "Unknown, Unknown"
        }
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Zero Trust Platform"}

# Simple endpoints for testing
@app.get("/security/analyze/admin")
def admin_view():
    return []

@app.get("/security/analyze/user/{username}")
def user_view(username: str):
    return {
        "user": username,
        "risk_score": 0,
        "risk_level": "LOW",
        "decision": "ALLOW",
        "signals": [],
        "total_logins": 0,
        "last_login": None,
        "accessible_resources": ["dashboard", "profile"]
    }

@app.get("/files/list/{username}")
def list_files(username: str):
    return []

@app.post("/files/access")
def file_access(request: Request):
    return {"status": "SUCCESS"}

@app.get("/admin/file-access")
def admin_files():
    return []

@app.get("/audit/chain")
def audit():
    return []
