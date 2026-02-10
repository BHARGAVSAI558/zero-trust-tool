# 🚀 Agent Deployment Guide

## Quick Installation (5 Minutes)

### Step 1: Download Agent
```bash
# Clone repository
git clone https://github.com/BHARGAVSAI558/zero_trust.git
cd zero_trust/agent
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run Agent
```bash
python zero_trust_agent.py <username>
```

Replace `<username>` with the employee's username (e.g., bhargav, john, sarah)

## 🏢 Enterprise Deployment

### Option 1: Windows Service (Recommended)

**Using NSSM (Non-Sucking Service Manager):**

1. Download NSSM: https://nssm.cc/download
2. Install as service:
```cmd
nssm install ZeroTrustAgent "C:\Python\python.exe" "C:\agent\zero_trust_agent.py" "username"
nssm set ZeroTrustAgent AppDirectory "C:\agent"
nssm set ZeroTrustAgent DisplayName "Zero Trust Security Agent"
nssm set ZeroTrustAgent Description "Monitors device activity for insider threats"
nssm start ZeroTrustAgent
```

3. Verify:
```cmd
nssm status ZeroTrustAgent
```

### Option 2: Linux Systemd Service

1. Create service file:
```bash
sudo nano /etc/systemd/system/zerotrust.service
```

2. Add configuration:
```ini
[Unit]
Description=Zero Trust Security Agent
After=network.target

[Service]
Type=simple
User=employee
WorkingDirectory=/opt/zerotrust/agent
ExecStart=/usr/bin/python3 /opt/zerotrust/agent/zero_trust_agent.py username
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable zerotrust
sudo systemctl start zerotrust
sudo systemctl status zerotrust
```

### Option 3: macOS LaunchAgent

1. Create plist file:
```bash
nano ~/Library/LaunchAgents/com.zerotrust.agent.plist
```

2. Add configuration:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.zerotrust.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/employee/zerotrust/agent/zero_trust_agent.py</string>
        <string>username</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/zerotrust.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/zerotrust.error.log</string>
</dict>
</plist>
```

3. Load agent:
```bash
launchctl load ~/Library/LaunchAgents/com.zerotrust.agent.plist
launchctl start com.zerotrust.agent
```

## 🔧 Configuration

Edit `zero_trust_agent.py` to customize:

```python
# Backend URL (change to your deployment)
BACKEND_URL = "https://zero-trust-3fmw.onrender.com"

# Check interval (seconds)
CHECK_INTERVAL = 300  # 5 minutes

# Sensitive paths to monitor
SENSITIVE_PATHS = [
    "Documents", 
    "Desktop", 
    "Downloads",
    "confidential",
    "secret",
    "private",
    "payroll",
    "hr",
    "finance"
]
```

## 📊 Monitoring

### Check Agent Status

**Windows:**
```cmd
sc query ZeroTrustAgent
```

**Linux:**
```bash
sudo systemctl status zerotrust
```

**macOS:**
```bash
launchctl list | grep zerotrust
```

### View Logs

**Windows:**
```cmd
type C:\agent\agent.log
```

**Linux:**
```bash
sudo journalctl -u zerotrust -f
```

**macOS:**
```bash
tail -f /tmp/zerotrust.log
```

## 🧪 Testing

### Test Agent Locally
```bash
# Run agent in foreground
python zero_trust_agent.py testuser

# In another terminal, run test suite
python test_agent.py
```

### Verify Backend Connection
```bash
curl https://zero-trust-3fmw.onrender.com/health
```

Expected response:
```json
{"status":"healthy","service":"Zero Trust Platform"}
```

## 🔒 Security Considerations

1. **No Admin Rights Required**: Agent runs with user privileges
2. **Encrypted Communication**: All data sent via HTTPS
3. **Minimal Data Collection**: Only security-relevant events
4. **No Password Storage**: Agent doesn't store credentials
5. **Tamper Detection**: Monitors own process integrity

## 📈 Scaling to Multiple Machines

### Using Group Policy (Windows Domain)

1. Create GPO for agent deployment
2. Copy agent files to network share
3. Create startup script:
```cmd
@echo off
if not exist "C:\Program Files\ZeroTrust\" (
    xcopy "\\server\share\agent" "C:\Program Files\ZeroTrust\" /E /I
    cd "C:\Program Files\ZeroTrust"
    pip install -r requirements.txt
    nssm install ZeroTrustAgent "C:\Python\python.exe" "C:\Program Files\ZeroTrust\zero_trust_agent.py" "%USERNAME%"
    nssm start ZeroTrustAgent
)
```

### Using Ansible (Linux)

```yaml
---
- name: Deploy Zero Trust Agent
  hosts: all
  become: yes
  tasks:
    - name: Install Python dependencies
      pip:
        name:
          - requests
          - psutil
        state: present
    
    - name: Copy agent files
      copy:
        src: agent/
        dest: /opt/zerotrust/agent/
        mode: '0755'
    
    - name: Create systemd service
      template:
        src: zerotrust.service.j2
        dest: /etc/systemd/system/zerotrust.service
    
    - name: Enable and start service
      systemd:
        name: zerotrust
        enabled: yes
        state: started
```

## 🆘 Troubleshooting

### Agent Won't Start

**Check Python version:**
```bash
python --version  # Must be 3.7+
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

### Can't Connect to Backend

**Test connectivity:**
```bash
curl https://zero-trust-3fmw.onrender.com/health
```

**Check firewall:**
- Ensure port 443 (HTTPS) is open
- Whitelist backend domain

### No Activity Detected

**Run with elevated privileges:**
```bash
# Windows (as Administrator)
python zero_trust_agent.py username

# Linux
sudo python3 zero_trust_agent.py username
```

**Check sensitive paths:**
- Verify SENSITIVE_PATHS matches your folder structure
- Add custom paths if needed

## 📞 Support

- GitHub Issues: https://github.com/BHARGAVSAI558/zero_trust/issues
- Documentation: See agent/README.md
- Backend Status: https://zero-trust-3fmw.onrender.com/health
