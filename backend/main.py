from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import os

def get_db():
    import psycopg2
    import psycopg2.extras
    return psycopg2.connect(os.getenv("DATABASE_URL", "postgresql://localhost/zero"))

app = FastAPI(title="Zero Trust Security Platform")

@app.on_event("startup")
async def startup_event():
    from init_db import init_database
    init_database()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/security/analyze/admin")
def admin_view():
    try:
        db = get_db()
        cursor = db.cursor(cursor_factory=__import__('psycopg2.extras', fromlist=['RealDictCursor']).RealDictCursor)
        cursor.execute("""
            SELECT DISTINCT user_id, 
            (SELECT COUNT(*) FROM login_logs WHERE user_id=l.user_id) as total_logins,
            (SELECT MAX(login_time) FROM login_logs WHERE user_id=l.user_id) as last_login
            FROM login_logs l
        """)
        users = cursor.fetchall()
        cursor.close()
        db.close()
        
        result = []
        for u in users:
            result.append({
                "user": u["user_id"],
                "risk_score": 15,
                "risk_level": "LOW",
                "decision": "ALLOW",
                "total_logins": u["total_logins"],
                "last_login": str(u["last_login"]) if u["last_login"] else None
            })
        return result
    except:
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

@app.post("/device/register")
async def register_device(request: Request):
    try:
        data = await request.json()
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO device_logs (user_id, device_id, mac_address, os, wifi_ssid, hostname, ip_address, trusted)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (data.get("username"), data.get("device_id"), data.get("mac_address"), 
              data.get("os"), data.get("wifi_ssid"), data.get("hostname"), 
              data.get("ip_address"), False))
        db.commit()
        cursor.close()
        db.close()
        return {"status": "SUCCESS"}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

@app.get("/files/list/{username}")
def list_files(username: str):
    return []

@app.post("/files/access")
async def file_access(request: Request):
    try:
        data = await request.json()
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO file_access_logs (user_id, file_name, action, ip_address)
            VALUES (%s,%s,%s,%s)
        """, (data.get("username"), data.get("file_name"), data.get("action"), data.get("ip_address")))
        db.commit()
        cursor.close()
        db.close()
        return {"status": "SUCCESS"}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

@app.get("/admin/file-access")
def admin_files():
    try:
        db = get_db()
        cursor = db.cursor(cursor_factory=__import__('psycopg2.extras', fromlist=['RealDictCursor']).RealDictCursor)
        cursor.execute("SELECT * FROM file_access_logs ORDER BY access_time DESC LIMIT 100")
        files = cursor.fetchall()
        cursor.close()
        db.close()
        return [{"user": f["user_id"], "file": f["file_name"], "action": f["action"], 
                 "time": str(f["access_time"]), "ip": f["ip_address"]} for f in files]
    except:
        return []

@app.get("/audit/chain")
def audit():
    return []
