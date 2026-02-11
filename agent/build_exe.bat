@echo off
REM Build Standalone Executable
REM Run this to create a .exe file that users can download and run

echo Installing PyInstaller...
pip install pyinstaller

echo Building executable...
pyinstaller --onefile --name "ZeroTrustAgent" --console zero_trust_agent.py

echo.
echo ============================================================
echo Build Complete!
echo ============================================================
echo.
echo Executable location: dist\ZeroTrustAgent.exe
echo.
echo Users can download and run this .exe file!
echo No Python installation required!
echo.
pause
