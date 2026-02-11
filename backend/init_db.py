import psycopg2
import os

def init_database():
    try:
        db_url = os.getenv("DATABASE_URL", "")
        if db_url and not db_url.startswith("postgresql://"):
            db_url = "postgresql://" + db_url
        
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(10) DEFAULT 'user',
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved_by VARCHAR(50),
                approved_at TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_logs (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(50) NOT NULL,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(45),
                success BOOLEAN DEFAULT FALSE,
                country VARCHAR(100) DEFAULT 'Unknown',
                city VARCHAR(100) DEFAULT 'Unknown'
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_logs (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(50) NOT NULL,
                device_id VARCHAR(255) UNIQUE,
                mac_address VARCHAR(17),
                os VARCHAR(50),
                trusted BOOLEAN DEFAULT FALSE,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                wifi_ssid VARCHAR(100),
                hostname VARCHAR(100),
                ip_address VARCHAR(45)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_access_logs (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(50) NOT NULL,
                file_name VARCHAR(255) NOT NULL,
                action VARCHAR(10) DEFAULT 'READ',
                ip_address VARCHAR(45),
                access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            INSERT INTO users (username, password, role, status) VALUES 
            ('admin', 'admin123', 'admin', 'active'),
            ('bhargav', 'admin123', 'user', 'active')
            ON CONFLICT (username) DO UPDATE SET status='active'
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database init error: {e}")

if __name__ == "__main__":
    init_database()
