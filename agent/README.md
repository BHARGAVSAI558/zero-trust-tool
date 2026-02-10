# 🕵️ Zero Trust Security Agent

Python agent that runs on employee workstations to monitor activity and detect insider threats.

## 🎯 What It Does

The agent monitors:
- **File Access**: Tracks access to sensitive files/folders
- **Login Behavior**: Detects odd-hour logins, weekend access
- **Network Activity**: Monitors external connections
- **USB Devices**: Detects removable drive connections
- **Device Changes**: Tracks hardware/network changes

## 🚀 Installation

### 1. Install Dependencies
```bash
cd agent
pip install -r requirements.txt
```

### 2. Run Agent
```bash
python zero_trust_agent.py <username>
```

Example:
```bash
python zero_trust_agent.py bhargav
```

## 📊 How It Works

```
Employee Machine
    ↓
[Agent Running 24/7]
    ↓ (every 5 minutes)
Collects: Files, Network, USB, Login Time
    ↓
Sends to Backend API
    ↓
Backend Calculates Risk Score
    ↓
Admin Dashboard Shows Threats
```

## 🔧 Configuration

Edit `zero_trust_agent.py` to customize:

```python
BACKEND_URL = "https://zero-trust-3fmw.onrender.com"  # Your backend
CHECK_INTERVAL = 300  # Check every 5 minutes
SENSITIVE_PATHS = ["Documents", "confidential", "payroll"]  # Monitor these
```

## 📈 Monitored Signals

1. **ODD_HOUR_LOGIN** - Login outside 8 AM - 6 PM
2. **WEEKEND_LOGIN** - Login on Saturday/Sunday
3. **EXCESSIVE_EXTERNAL_CONNECTIONS** - >10 external IPs
4. **USB_DEVICE_CONNECTED** - Removable drive detected
5. **SENSITIVE_FILE_ACCESS** - Access to confidential files

## 🏢 Enterprise Deployment

### Windows (Run as Service)
```bash
# Install as Windows Service
nssm install ZeroTrustAgent "C:\Python\python.exe" "C:\agent\zero_trust_agent.py" "username"
nssm start ZeroTrustAgent
```

### Linux (Systemd)
```bash
# Create service file
sudo nano /etc/systemd/system/zerotrust.service

[Unit]
Description=Zero Trust Security Agent
After=network.target

[Service]
Type=simple
User=employee
ExecStart=/usr/bin/python3 /opt/agent/zero_trust_agent.py username
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable zerotrust
sudo systemctl start zerotrust
```

### macOS (LaunchAgent)
```bash
# Create plist file
nano ~/Library/LaunchAgents/com.zerotrust.agent.plist

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.zerotrust.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/employee/agent/zero_trust_agent.py</string>
        <string>username</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>

# Load agent
launchctl load ~/Library/LaunchAgents/com.zerotrust.agent.plist
```

## 🔒 Security Features

- **Device Fingerprinting**: Unique ID per machine
- **Encrypted Communication**: HTTPS to backend
- **Minimal Permissions**: No admin rights needed
- **Tamper Detection**: Monitors own process
- **Offline Mode**: Caches data if backend unavailable

## 📊 Output Example

```
============================================================
Zero Trust Security Agent v1.0
============================================================
User: bhargav
Device ID: a3f5c8d2e1b4f7a9
Backend: https://zero-trust-3fmw.onrender.com
Check Interval: 300s
============================================================

[OK] Device registered: LAPTOP-ABC123

[OK] Agent started. Monitoring activity...

[14:23:45] Cycle #1
  No suspicious activity detected

[14:28:45] Cycle #2
[OK] Sent 3 file access logs
[ALERT] Detected anomalies: USB_DEVICE_CONNECTED

[14:33:45] Cycle #3
[ALERT] Detected anomalies: EXCESSIVE_EXTERNAL_CONNECTIONS
```

## 🧪 Testing

Test the agent locally:
```bash
# Run for 1 minute
python zero_trust_agent.py testuser

# Open some files in Documents folder
# Connect a USB drive
# Check backend dashboard for alerts
```

## 🆚 vs Microsoft Defender ATP Agent

| Feature | Zero Trust Agent | MS Defender |
|---------|-----------------|-------------|
| **Size** | 50 KB | 500+ MB |
| **CPU Usage** | <1% | 5-10% |
| **Memory** | 20 MB | 200+ MB |
| **Signals** | 13 | 100+ |
| **Customizable** | Yes | No |
| **Cost** | Free | $5-10/user/month |

## 🔧 Troubleshooting

**Agent won't start:**
```bash
# Check Python version (3.7+)
python --version

# Install dependencies
pip install -r requirements.txt
```

**Can't connect to backend:**
```bash
# Test backend connectivity
curl https://zero-trust-3fmw.onrender.com/health

# Check firewall rules
# Ensure port 443 (HTTPS) is open
```

**No file access detected:**
```bash
# Run with admin privileges (Windows)
python zero_trust_agent.py username

# Check SENSITIVE_PATHS configuration
```

## 📝 License

MIT License - See LICENSE file
