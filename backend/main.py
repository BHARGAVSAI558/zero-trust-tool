from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, time as dt_time
import os
import requests
import hashlib
import json

def get_db():
    import psycopg2
    import psycopg2.extras
    db_url = os.getenv("DATABASE_URL", "postgresql://localhost/zero")
    if db_url and not db_url.startswith("postgresql://"):
        db_url = "postgresql://" + db_url
    return psycopg2.connect(db_url)

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

def get_geolocation(ip):
    try:
        # Use ipapi.co for exact location
        geo = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5).json()
        if not geo.get('error'):
            return {
                "country": geo.get("country_name", "Unknown"),
                "city": geo.get("city", "Unknown"),
                "region": geo.get("region", "Unknown"),
                "latitude": geo.get("latitude", 0),
                "longitude": geo.get("longitude", 0),
                "timezone": geo.get("timezone", "Unknown"),
                "isp": geo.get("org", "Unknown"),
                "ip": geo.get("ip", ip),
                "postal": geo.get("postal", "Unknown")
            }
    except:
        pass
    return {
        "country": "Unknown",
        "city": "Unknown",
        "region": "Unknown",
        "latitude": 0,
        "longitude": 0,
        "timezone": "Unknown",
        "isp": "Unknown",
        "ip": ip,
        "postal": "Unknown"
    }

# Blockchain for audit trail
class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(proof=1, previous_hash='0')
    
    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'data': []
        }
        self.chain.append(block)
        return block
    
    def add_transaction(self, transaction):
        if self.chain:
            self.chain[-1]['data'].append(transaction)
    
    def get_previous_block(self):
        return self.chain[-1] if self.chain else None
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        while True:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                return new_proof
            new_proof += 1
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

blockchain = Blockchain()

# UEBA Risk Scoring Engine
def calculate_risk_score(username, db):
    """Calculate risk score based on UEBA signals"""
    risk_score = 0
    signals = []
    
    cursor = db.cursor(cursor_factory=__import__('psycopg2.extras', fromlist=['RealDictCursor']).RealDictCursor)
    
    # 1. Check odd-hour logins (outside 8 AM - 6 PM)
    cursor.execute("""
        SELECT COUNT(*) as count FROM login_logs 
        WHERE user_id=%s AND (EXTRACT(HOUR FROM login_time) < 8 OR EXTRACT(HOUR FROM login_time) > 18)
        AND login_time > NOW() - INTERVAL '24 hours'
    """, (username,))
    odd_hours = cursor.fetchone()['count']
    if odd_hours > 0:
        risk_score += odd_hours * 5
        signals.append(f"ODD_HOUR_LOGIN ({odd_hours} times)")
    
    # 2. Check failed login attempts
    cursor.execute("""
        SELECT COUNT(*) as count FROM login_logs 
        WHERE user_id=%s AND success=false AND login_time > NOW() - INTERVAL '1 hour'
    """, (username,))
    failed = cursor.fetchone()['count']
    if failed > 3:
        risk_score += 15
        signals.append(f"FAILED_LOGIN_ATTEMPTS ({failed})")
    
    # 3. Check multiple IPs
    cursor.execute("""
        SELECT COUNT(DISTINCT ip_address) as count FROM login_logs 
        WHERE user_id=%s AND login_time > NOW() - INTERVAL '1 hour'
    """, (username,))
    ips = cursor.fetchone()['count']
    if ips > 2:
        risk_score += 10
        signals.append(f"MULTIPLE_IPS ({ips})")
    
    # 4. Check weekend access
    cursor.execute("""
        SELECT COUNT(*) as count FROM login_logs 
        WHERE user_id=%s AND EXTRACT(DOW FROM login_time) IN (0,6)
        AND login_time > NOW() - INTERVAL '7 days'
    """, (username,))
    weekend = cursor.fetchone()['count']
    if weekend > 0:
        risk_score += weekend * 3
        signals.append(f"WEEKEND_ACCESS ({weekend} times)")
    
    # 5. Check unknown devices
    cursor.execute("""
        SELECT COUNT(*) as count FROM device_logs 
        WHERE user_id=%s AND trusted=false
    """, (username,))
    untrusted = cursor.fetchone()['count']
    if untrusted > 0:
        risk_score += untrusted * 10
        signals.append(f"UNTRUSTED_DEVICES ({untrusted})")
    
    # 6. Check sensitive file access
    cursor.execute("""
        SELECT COUNT(*) as count FROM file_access_logs 
        WHERE user_id=%s AND access_time > NOW() - INTERVAL '24 hours'
    """, (username,))
    files = cursor.fetchone()['count']
    if files > 50:
        risk_score += 15
        signals.append(f"EXCESSIVE_FILE_ACCESS ({files})")
    
    # 7. Check file deletions
    cursor.execute("""
        SELECT COUNT(*) as count FROM file_access_logs 
        WHERE user_id=%s AND action='DELETE' AND access_time > NOW() - INTERVAL '24 hours'
    """, (username,))
    deletions = cursor.fetchone()['count']
    if deletions > 5:
        risk_score += 20
        signals.append(f"FILE_DELETIONS ({deletions})")
    
    cursor.close()
    
    # Cap at 100
    risk_score = min(risk_score, 100)
    
    # Determine risk level and decision
    if risk_score <= 30:
        risk_level = "LOW"
        decision = "ALLOW"
        zone = "CRITICAL"
    elif risk_score <= 50:
        risk_level = "MEDIUM"
        decision = "RESTRICT"
        zone = "SENSITIVE"
    elif risk_score <= 70:
        risk_level = "HIGH"
        decision = "RESTRICT"
        zone = "INTERNAL"
    else:
        risk_level = "CRITICAL"
        decision = "DENY"
        zone = "PUBLIC"
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "decision": decision,
        "zone": zone,
        "signals": signals
    }

@app.post("/auth/register")
async def register(request: Request, username: str = Form(...), password: str = Form(...)):
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        if cursor.fetchone():
            cursor.close()
            db.close()
            return {"status": "FAIL", "message": "Username already exists"}
        
        cursor.execute("""
            INSERT INTO users (username, password, role, status)
            VALUES (%s, %s, 'user', 'pending')
        """, (username, password))
        db.commit()
        cursor.close()
        db.close()
        
        return {"status": "SUCCESS", "message": "Registration pending admin approval"}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

@app.post("/auth/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    try:
        db = get_db()
        cursor = db.cursor(cursor_factory=__import__('psycopg2.extras', fromlist=['RealDictCursor']).RealDictCursor)
        
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            db.close()
            return {"status": "FAIL", "message": "Invalid credentials"}
        
        if user["status"] == "pending":
            cursor.close()
            db.close()
            return {"status": "FAIL", "message": "Account pending admin approval"}
        
        if user["status"] == "revoked":
            cursor.close()
            db.close()
            return {"status": "FAIL", "message": "Access revoked by admin"}
        
        success = True
        ip = request.client.host if request.client else "Unknown"
        
        geo = get_geolocation(ip)
        
        cursor.execute("""
            INSERT INTO login_logs (user_id, login_time, ip_address, success, country, city)
            VALUES (%s, NOW(), %s, %s, %s, %s)
        """, (username, geo["ip"], success, geo["country"], geo["city"]))
        db.commit()
        
        blockchain.add_transaction({
            "type": "LOGIN",
            "user": username,
            "success": success,
            "ip": geo["ip"],
            "location": f"{geo['city']}, {geo['country']}",
            "latitude": geo["latitude"],
            "longitude": geo["longitude"],
            "timestamp": str(datetime.now())
        })
        
        if len(blockchain.chain[-1]['data']) >= 3:
            previous_block = blockchain.get_previous_block()
            previous_proof = previous_block['proof']
            proof = blockchain.proof_of_work(previous_proof)
            previous_hash = blockchain.hash(previous_block)
            blockchain.create_block(proof, previous_hash)
        
        risk_data = calculate_risk_score(username, db)
        
        cursor.close()
        db.close()
        
        return {
            "status": "SUCCESS",
            "user": username,
            "role": user["role"],
            "location": f"{geo['city']}, {geo['country']}",
            "latitude": geo["latitude"],
            "longitude": geo["longitude"],
            "timezone": geo["timezone"],
            "isp": geo["isp"],
            "risk_score": risk_data["risk_score"],
            "risk_level": risk_data["risk_level"],
            "decision": risk_data["decision"],
            "access_zone": risk_data["zone"]
        }
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

@app.post("/admin/approve-user")
async def approve_user(username: str = Form(...), admin: str = Form(...), action: str = Form(...)):
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT role FROM users WHERE username=%s", (admin,))
        admin_user = cursor.fetchone()
        if not admin_user or admin_user[0] != 'admin':
            cursor.close()
            db.close()
            return {"status": "FAIL", "message": "Unauthorized"}
        
        if action == "approve":
            cursor.execute("""
                UPDATE users SET status='active', approved_by=%s, approved_at=NOW()
                WHERE username=%s
            """, (admin, username))
        else:
            cursor.execute("DELETE FROM users WHERE username=%s AND status='pending'", (username,))
        
        db.commit()
        cursor.close()
        db.close()
        
        return {"status": "SUCCESS", "message": f"User {action}d successfully"}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

@app.post("/admin/revoke-access")
async def revoke_access(username: str = Form(...), admin: str = Form(...)):
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT role FROM users WHERE username=%s", (admin,))
        admin_user = cursor.fetchone()
        if not admin_user or admin_user[0] != 'admin':
            cursor.close()
            db.close()
            return {"status": "FAIL", "message": "Unauthorized"}
        
        if username in ['admin', 'bhargav']:
            cursor.close()
            db.close()
            return {"status": "FAIL", "message": "Cannot revoke protected users"}
        
        cursor.execute("UPDATE users SET status='revoked' WHERE username=%s", (username,))
        db.commit()
        cursor.close()
        db.close()
        
        return {"status": "SUCCESS", "message": "Access revoked"}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

@app.get("/admin/pending-users")
def get_pending_users():
    try:
        db = get_db()
        cursor = db.cursor(cursor_factory=__import__('psycopg2.extras', fromlist=['RealDictCursor']).RealDictCursor)
        cursor.execute("""
            SELECT username, created_at FROM users WHERE status='pending' ORDER BY created_at DESC
        """)
        users = cursor.fetchall()
        cursor.close()
        db.close()
        return [{"username": u["username"], "created_at": str(u["created_at"])} for u in users]
    except:
        return []

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Zero Trust Platform"}

@app.get("/security/analyze/admin")
def admin_view():
    try:
        db = get_db()
        cursor = db.cursor(cursor_factory=__import__('psycopg2.extras', fromlist=['RealDictCursor']).RealDictCursor)
        cursor.execute("""
            SELECT DISTINCT l.user_id,
            (SELECT COUNT(*) FROM login_logs WHERE user_id=l.user_id) as total_logins,
            (SELECT MAX(login_time) FROM login_logs WHERE user_id=l.user_id) as last_login,
            (SELECT ip_address FROM login_logs WHERE user_id=l.user_id ORDER BY login_time DESC LIMIT 1) as ip_address,
            (SELECT country FROM login_logs WHERE user_id=l.user_id ORDER BY login_time DESC LIMIT 1) as country,
            (SELECT city FROM login_logs WHERE user_id=l.user_id ORDER BY login_time DESC LIMIT 1) as city,
            (SELECT mac_address FROM device_logs WHERE user_id=l.user_id ORDER BY first_seen DESC LIMIT 1) as mac_address,
            (SELECT wifi_ssid FROM device_logs WHERE user_id=l.user_id ORDER BY first_seen DESC LIMIT 1) as wifi_ssid,
            (SELECT hostname FROM device_logs WHERE user_id=l.user_id ORDER BY first_seen DESC LIMIT 1) as hostname,
            (SELECT os FROM device_logs WHERE user_id=l.user_id ORDER BY first_seen DESC LIMIT 1) as os,
            (SELECT status FROM users WHERE username=l.user_id) as status
            FROM login_logs l
        """)
        users = cursor.fetchall()
        
        result = []
        for u in users:
            risk_data = calculate_risk_score(u["user_id"], db)
            
            result.append({
                "user": u["user_id"] or "unknown",
                "risk_score": risk_data["risk_score"],
                "risk_level": risk_data["risk_level"],
                "decision": risk_data["decision"],
                "access_zone": risk_data["zone"],
                "total_logins": u["total_logins"] or 0,
                "last_login": str(u["last_login"]) if u["last_login"] else None,
                "signals": risk_data["signals"],
                "ip_address": u["ip_address"] or "N/A",
                "country": u["country"] or "Unknown",
                "city": u["city"] or "Unknown",
                "mac_address": u["mac_address"] or "N/A",
                "wifi_ssid": u["wifi_ssid"] or "N/A",
                "hostname": u["hostname"] or "N/A",
                "os": u["os"] or "N/A",
                "status": u["status"] or "active"
            })
        
        cursor.close()
        db.close()
        return result
    except Exception as e:
        print(f"Admin view error: {e}")
        import traceback
        traceback.print_exc()
        return []

@app.get("/security/analyze/user/{username}")
def user_view(username: str):
    try:
        db = get_db()
        cursor = db.cursor(cursor_factory=__import__('psycopg2.extras', fromlist=['RealDictCursor']).RealDictCursor)
        
        cursor.execute("SELECT COUNT(*) as total FROM login_logs WHERE user_id=%s", (username,))
        total = cursor.fetchone()["total"]
        
        cursor.execute("SELECT * FROM login_logs WHERE user_id=%s ORDER BY login_time DESC LIMIT 1", (username,))
        last_login = cursor.fetchone()
        
        cursor.execute("SELECT * FROM device_logs WHERE user_id=%s ORDER BY first_seen DESC LIMIT 1", (username,))
        device = cursor.fetchone()
        
        cursor.close()
        db.close()
        
        return {
            "user": username,
            "risk_score": 15,
            "risk_level": "LOW",
            "decision": "ALLOW",
            "signals": [],
            "total_logins": total,
            "last_login": str(last_login["login_time"]) if last_login else None,
            "accessible_resources": ["dashboard", "profile", "reports", "analytics"],
            "ip_address": device["ip_address"] if device else "N/A",
            "mac_address": device["mac_address"] if device else "N/A",
            "wifi_ssid": device["wifi_ssid"] if device else "N/A",
            "hostname": device["hostname"] if device else "N/A",
            "os": device["os"] if device else "N/A",
            "country": last_login["country"] if last_login else "Unknown",
            "city": last_login["city"] if last_login else "Unknown"
        }
    except:
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
        ip = request.client.host if request.client else data.get("ip_address", "Unknown")
        
        geo = get_geolocation(ip)
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            INSERT INTO device_logs (user_id, device_id, mac_address, os, wifi_ssid, hostname, ip_address, trusted, first_seen)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s, NOW())
            ON CONFLICT (device_id) DO UPDATE SET
                ip_address = EXCLUDED.ip_address,
                wifi_ssid = EXCLUDED.wifi_ssid,
                first_seen = NOW()
        """, (data.get("username"), data.get("device_id"), data.get("mac_address"), 
              data.get("os"), data.get("wifi_ssid"), data.get("hostname"), 
              geo["ip"], False))
        db.commit()
        cursor.close()
        db.close()
        
        return {
            "status": "SUCCESS",
            "location": f"{geo['city']}, {geo['country']}",
            "timezone": geo["timezone"]
        }
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

@app.get("/files/list/{username}")
def list_files(username: str):
    try:
        db = get_db()
        cursor = db.cursor(cursor_factory=__import__('psycopg2.extras', fromlist=['RealDictCursor']).RealDictCursor)
        cursor.execute("SELECT * FROM file_access_logs WHERE user_id=%s ORDER BY access_time DESC LIMIT 50", (username,))
        files = cursor.fetchall()
        cursor.close()
        db.close()
        return files
    except:
        return []

@app.post("/files/access")
async def file_access(request: Request):
    try:
        data = await request.json()
        db = get_db()
        cursor = db.cursor()
        ip = request.client.host if request.client else "Unknown"
        
        cursor.execute("""
            INSERT INTO file_access_logs (user_id, file_name, action, ip_address, access_time)
            VALUES (%s,%s,%s,%s, NOW())
        """, (data.get("user_id"), data.get("file_name"), data.get("action"), ip))
        db.commit()
        cursor.close()
        db.close()
        return {"status": "SUCCESS", "timestamp": datetime.now().isoformat()}
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
        return [{
            "user_id": f["user_id"], 
            "file_name": f["file_name"], 
            "action": f["action"], 
            "access_time": str(f["access_time"]), 
            "ip_address": f["ip_address"]
        } for f in files]
    except:
        return []

@app.get("/audit/chain")
def audit():
    """Get blockchain audit trail"""
    try:
        blocks_with_hash = []
        for block in blockchain.chain[-10:]:
            block_copy = block.copy()
            block_copy['hash'] = blockchain.hash(block)
            blocks_with_hash.append(block_copy)
        
        return blocks_with_hash
    except Exception as e:
        print(f"Audit chain error: {e}")
        return []

@app.get("/zones")
def get_zones():
    """Get micro-segmentation zones"""
    return {
        "zones": [
            {
                "name": "PUBLIC",
                "risk_threshold": 100,
                "resources": ["Company Website", "Public Docs", "General Info"],
                "description": "Accessible to all users"
            },
            {
                "name": "INTERNAL",
                "risk_threshold": 70,
                "resources": ["Email", "Calendar", "Team Chat", "Project Management"],
                "description": "Internal business resources"
            },
            {
                "name": "SENSITIVE",
                "risk_threshold": 50,
                "resources": ["Customer Data", "Financial Reports", "HR Records", "Source Code"],
                "description": "Confidential business data"
            },
            {
                "name": "CRITICAL",
                "risk_threshold": 30,
                "resources": ["Payment Systems", "Database Credentials", "Encryption Keys", "Executive Comms"],
                "description": "Highest security assets"
            }
        ]
    }
