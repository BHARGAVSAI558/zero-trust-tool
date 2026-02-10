# 🚀 Zero Trust Agent - Quick Install

## One-Line Installation

### Windows (PowerShell - Run as Administrator)
```powershell
irm https://raw.githubusercontent.com/BHARGAVSAI558/zero_trust/main/agent/install_windows.bat | iex
```

Or download and run:
```powershell
curl -o install.bat https://raw.githubusercontent.com/BHARGAVSAI558/zero_trust/main/agent/install_windows.bat && install.bat
```

### Linux/Mac (Terminal)
```bash
curl -fsSL https://raw.githubusercontent.com/BHARGAVSAI558/zero_trust/main/agent/install_linux.sh | sudo bash
```

Or download and run:
```bash
wget https://raw.githubusercontent.com/BHARGAVSAI558/zero_trust/main/agent/install_linux.sh
chmod +x install_linux.sh
sudo ./install_linux.sh
```

## Manual Installation (All Platforms)

### Step 1: Download Agent
```bash
# Clone repository
git clone https://github.com/BHARGAVSAI558/zero_trust.git
cd zero_trust/agent
```

Or download directly:
- Windows: https://github.com/BHARGAVSAI558/zero_trust/archive/refs/heads/main.zip
- Extract and navigate to `agent` folder

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run Agent
```bash
python zero_trust_agent.py <your_username>
```

Example:
```bash
python zero_trust_agent.py john
```

## 📦 What Gets Installed

- **Agent Script**: `zero_trust_agent.py` (50 KB)
- **Dependencies**: `psutil`, `requests` (~5 MB)
- **Location**: 
  - Windows: `C:\Program Files\ZeroTrustAgent\`
  - Linux: `/opt/zerotrust/`
  - Mac: `/opt/zerotrust/`

## 🔧 Post-Installation

### Run Agent Manually
```bash
# Windows
cd "C:\Program Files\ZeroTrustAgent"
python zero_trust_agent.py username

# Linux/Mac
cd /opt/zerotrust
python3 zero_trust_agent.py username
```

### Install as Service (Auto-start)

**Windows (using NSSM):**
1. Download NSSM: https://nssm.cc/download
2. Install service:
```cmd
nssm install ZeroTrustAgent python.exe "C:\Program Files\ZeroTrustAgent\zero_trust_agent.py" username
nssm start ZeroTrustAgent
```

**Linux (systemd):**
```bash
sudo nano /etc/systemd/system/zerotrust.service
```
Add:
```ini
[Unit]
Description=Zero Trust Agent
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/zerotrust/zero_trust_agent.py username
Restart=always

[Install]
WantedBy=multi-user.target
```
Enable:
```bash
sudo systemctl enable zerotrust
sudo systemctl start zerotrust
```

## 🌐 Access Dashboard

After installation, view your security status:
- **Dashboard**: https://zer0-trust.netlify.app
- **Login**: Use your username
- **Admin**: admin / admin123

## ✅ Verify Installation

```bash
# Check if agent is running
# Windows
tasklist | findstr python

# Linux/Mac
ps aux | grep zero_trust_agent
```

## 🆘 Troubleshooting

**Python not found:**
- Install Python 3.7+: https://www.python.org/downloads/

**Permission denied:**
- Windows: Run as Administrator
- Linux/Mac: Use `sudo`

**Can't connect to backend:**
```bash
curl https://zero-trust-3fmw.onrender.com/health
```
Should return: `{"status":"healthy"}`

## 📊 System Requirements

- **OS**: Windows 7+, Linux (any), macOS 10.12+
- **Python**: 3.7 or higher
- **RAM**: 50 MB
- **Disk**: 10 MB
- **Network**: Internet connection for backend communication

## 🔒 Security

- Agent runs with user privileges (no admin required)
- All communication via HTTPS
- No passwords stored locally
- Open source - audit the code!

## 📞 Support

- **Issues**: https://github.com/BHARGAVSAI558/zero_trust/issues
- **Documentation**: See README.md
- **Backend Status**: https://zero-trust-3fmw.onrender.com/health
