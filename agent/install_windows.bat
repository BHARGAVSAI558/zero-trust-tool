@echo off
REM Zero Trust Agent Installer for Windows
REM Downloads and installs the agent automatically

echo ============================================================
echo Zero Trust Security Agent - Installer
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.7+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python detected
echo.

REM Create installation directory
set INSTALL_DIR=%ProgramFiles%\ZeroTrustAgent
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo [INFO] Installing to: %INSTALL_DIR%
echo.

REM Download agent files from GitHub
echo [INFO] Downloading agent files...
curl -L -o "%INSTALL_DIR%\zero_trust_agent.py" https://raw.githubusercontent.com/BHARGAVSAI558/zero_trust/main/agent/zero_trust_agent.py
curl -L -o "%INSTALL_DIR%\requirements.txt" https://raw.githubusercontent.com/BHARGAVSAI558/zero_trust/main/agent/requirements.txt

if not exist "%INSTALL_DIR%\zero_trust_agent.py" (
    echo [ERROR] Failed to download agent files
    pause
    exit /b 1
)

echo [OK] Files downloaded
echo.

REM Install dependencies
echo [INFO] Installing dependencies...
cd "%INSTALL_DIR%"
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [OK] Dependencies installed
echo.

REM Get username
set /p USERNAME="Enter your username: "

echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo To start the agent, run:
echo   cd "%INSTALL_DIR%"
echo   python zero_trust_agent.py %USERNAME%
echo.
echo Or install as Windows Service (requires admin):
echo   nssm install ZeroTrustAgent python.exe "%INSTALL_DIR%\zero_trust_agent.py" %USERNAME%
echo   nssm start ZeroTrustAgent
echo.
pause
