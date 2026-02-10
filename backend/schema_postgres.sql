-- PostgreSQL Schema for Zero Trust Platform

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(10) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS login_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    success BOOLEAN DEFAULT FALSE,
    country VARCHAR(100) DEFAULT 'Unknown',
    city VARCHAR(100) DEFAULT 'Unknown'
);

CREATE INDEX IF NOT EXISTS idx_login_user ON login_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_login_time ON login_logs(login_time);

CREATE TABLE IF NOT EXISTS device_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    device_id VARCHAR(255),
    mac_address VARCHAR(17),
    os VARCHAR(50),
    trusted BOOLEAN DEFAULT FALSE,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    wifi_ssid VARCHAR(100),
    hostname VARCHAR(100),
    ip_address VARCHAR(45)
);

CREATE INDEX IF NOT EXISTS idx_device_user ON device_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_device_id ON device_logs(device_id);

CREATE TABLE IF NOT EXISTS file_access_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    action VARCHAR(10) DEFAULT 'READ',
    ip_address VARCHAR(45),
    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_file_user ON file_access_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_file_time ON file_access_logs(access_time);

-- Insert default users (plain passwords for testing)
INSERT INTO users (username, password, role) VALUES 
('admin', 'admin123', 'admin'),
('bhargav', 'admin123', 'user')
ON CONFLICT (username) DO NOTHING;
