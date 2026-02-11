@echo off
echo Building Zero Trust Agent GUI...
pip install pyinstaller
python -m PyInstaller --onefile --windowed --name "ZeroTrustAgent" --icon=NONE zero_trust_gui.py
echo.
echo Done! Executable: dist\ZeroTrustAgent.exe
pause
