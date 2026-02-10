#!/bin/bash
# Zero Trust Agent Installer for Linux/Mac
# Downloads and installs the agent automatically

echo "============================================================"
echo "Zero Trust Security Agent - Installer"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed!"
    echo "Please install Python 3.7+ first"
    exit 1
fi

echo "[OK] Python detected: $(python3 --version)"
echo ""

# Create installation directory
INSTALL_DIR="/opt/zerotrust"
sudo mkdir -p "$INSTALL_DIR"

echo "[INFO] Installing to: $INSTALL_DIR"
echo ""

# Download agent files from GitHub
echo "[INFO] Downloading agent files..."
sudo curl -L -o "$INSTALL_DIR/zero_trust_agent.py" https://raw.githubusercontent.com/BHARGAVSAI558/zero_trust/main/agent/zero_trust_agent.py
sudo curl -L -o "$INSTALL_DIR/requirements.txt" https://raw.githubusercontent.com/BHARGAVSAI558/zero_trust/main/agent/requirements.txt

if [ ! -f "$INSTALL_DIR/zero_trust_agent.py" ]; then
    echo "[ERROR] Failed to download agent files"
    exit 1
fi

echo "[OK] Files downloaded"
echo ""

# Install dependencies
echo "[INFO] Installing dependencies..."
sudo python3 -m pip install -r "$INSTALL_DIR/requirements.txt"

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    exit 1
fi

echo "[OK] Dependencies installed"
echo ""

# Get username
read -p "Enter your username: " USERNAME

echo ""
echo "============================================================"
echo "Installation Complete!"
echo "============================================================"
echo ""
echo "To start the agent, run:"
echo "  cd $INSTALL_DIR"
echo "  python3 zero_trust_agent.py $USERNAME"
echo ""
echo "Or install as systemd service:"
echo "  sudo systemctl enable zerotrust"
echo "  sudo systemctl start zerotrust"
echo ""
