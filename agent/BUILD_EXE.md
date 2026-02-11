# 🔨 Build Windows .EXE Installer

## Quick Build

Run this command in the `agent` folder:

```cmd
build_exe.bat
```

This will create `dist\ZeroTrustAgent.exe` - a standalone executable!

## Manual Build Steps

```cmd
cd e:\zero-trust-tool\agent
pip install pyinstaller
pyinstaller --onefile --name "ZeroTrustAgent" --console zero_trust_agent.py
```

## Output

- **File**: `dist\ZeroTrustAgent.exe`
- **Size**: ~15-20 MB (includes Python + dependencies)
- **Portable**: No Python installation needed!

## Distribution

Upload `ZeroTrustAgent.exe` to:
1. **GitHub Releases**: https://github.com/BHARGAVSAI558/zero-trust-tool/releases
2. **Google Drive**: Share link with users
3. **Dropbox**: Public download link

## Usage

Users simply:
1. Download `ZeroTrustAgent.exe`
2. Double-click to run
3. Enter their username when prompted

Just like Autopsy! 🎉
