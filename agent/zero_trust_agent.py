#!/usr/bin/env python3
"""
Zero Trust Security Agent
Runs on employee workstations to monitor activity and send telemetry to backend
"""

import os
import sys
import time
import socket
import platform
import uuid
import hashlib
import requests
import json
from datetime import datetime
from pathlib import Path
import psutil

# Configuration
BACKEND_URL = "https://zero-trust-3fmw.onrender.com"
USERNAME = None  # Set via command line
CHECK_INTERVAL = 300  # 5 minutes
SENSITIVE_PATHS = [
    "Documents", "Desktop", "Downloads", 
    "confidential", "secret", "private", "payroll", "hr"
]

class ZeroTrustAgent:
    def __init__(self, username):
        self.username = username
        self.device_id = self.get_device_id()
        self.last_login_time = datetime.now()
        self.file_access_cache = set()
        
    def get_device_id(self):
        """Generate unique device fingerprint"""
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
        hostname = socket.gethostname()
        return hashlib.sha256(f"{mac}-{hostname}".encode()).hexdigest()[:16]
    
    def get_device_info(self):
        """Collect device information"""
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
            hostname = socket.gethostname()
            os_info = f"{platform.system()} {platform.release()}"
            ip = socket.gethostbyname(hostname)
            
            # Get WiFi SSID (Windows)
            wifi_ssid = "Unknown"
            if platform.system() == "Windows":
                try:
                    import subprocess
                    result = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces'], encoding='utf-8')
                    for line in result.split('\n'):
                        if 'SSID' in line and 'BSSID' not in line:
                            wifi_ssid = line.split(':')[1].strip()
                            break
                except:
                    pass
            
            return {
                "username": self.username,
                "device_id": self.device_id,
                "mac_address": mac,
                "hostname": hostname,
                "os": os_info,
                "wifi_ssid": wifi_ssid,
                "ip_address": ip
            }
        except Exception as e:
            print(f"[ERROR] Failed to get device info: {e}")
            return None
    
    def register_device(self):
        """Register device with backend"""
        device_info = self.get_device_info()
        if not device_info:
            return False
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/device/register",
                json=device_info,
                timeout=10
            )
            if response.status_code == 200:
                print(f"[OK] Device registered: {device_info['hostname']}")
                return True
            else:
                print(f"[WARN] Device registration failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] Cannot connect to backend: {e}")
            return False
    
    def monitor_file_access(self):
        """Monitor file system access"""
        suspicious_files = []
        
        try:
            # Monitor recent file operations
            for proc in psutil.process_iter(['pid', 'name', 'open_files']):
                try:
                    if proc.info['open_files']:
                        for file in proc.info['open_files']:
                            file_path = file.path.lower()
                            
                            # Check if accessing sensitive paths
                            if any(sensitive in file_path for sensitive in SENSITIVE_PATHS):
                                file_key = f"{file.path}-{datetime.now().strftime('%Y%m%d%H')}"
                                if file_key not in self.file_access_cache:
                                    suspicious_files.append({
                                        "file_name": file.path,
                                        "action": "READ",
                                        "process": proc.info['name']
                                    })
                                    self.file_access_cache.add(file_key)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"[ERROR] File monitoring failed: {e}")
        
        return suspicious_files
    
    def check_login_anomalies(self):
        """Detect login anomalies"""
        anomalies = []
        current_hour = datetime.now().hour
        
        # Check odd hours (outside 8 AM - 6 PM)
        if current_hour < 8 or current_hour > 18:
            anomalies.append("ODD_HOUR_LOGIN")
        
        # Check if weekend
        if datetime.now().weekday() >= 5:
            anomalies.append("WEEKEND_LOGIN")
        
        return anomalies
    
    def check_network_anomalies(self):
        """Detect network anomalies"""
        anomalies = []
        
        try:
            # Check for external connections
            connections = psutil.net_connections(kind='inet')
            external_ips = set()
            
            for conn in connections:
                if conn.raddr and conn.status == 'ESTABLISHED':
                    remote_ip = conn.raddr.ip
                    # Check if external (not private IP)
                    if not (remote_ip.startswith('10.') or 
                           remote_ip.startswith('192.168.') or 
                           remote_ip.startswith('172.')):
                        external_ips.add(remote_ip)
            
            if len(external_ips) > 10:
                anomalies.append("EXCESSIVE_EXTERNAL_CONNECTIONS")
        except Exception as e:
            print(f"[ERROR] Network check failed: {e}")
        
        return anomalies
    
    def check_usb_devices(self):
        """Monitor USB device connections"""
        anomalies = []
        
        try:
            # Check for removable drives
            partitions = psutil.disk_partitions()
            for partition in partitions:
                if 'removable' in partition.opts.lower():
                    anomalies.append("USB_DEVICE_CONNECTED")
                    break
        except Exception as e:
            print(f"[ERROR] USB check failed: {e}")
        
        return anomalies
    
    def send_telemetry(self, files, anomalies):
        """Send collected data to backend"""
        try:
            # Send file access logs
            for file_data in files:
                requests.post(
                    f"{BACKEND_URL}/files/access",
                    json={
                        "user_id": self.username,
                        "file_name": file_data["file_name"],
                        "action": file_data["action"]
                    },
                    timeout=5
                )
            
            if files:
                print(f"[OK] Sent {len(files)} file access logs")
            
            if anomalies:
                print(f"[ALERT] Detected anomalies: {', '.join(anomalies)}")
        
        except Exception as e:
            print(f"[ERROR] Failed to send telemetry: {e}")
    
    def run(self):
        """Main monitoring loop"""
        print(f"=" * 60)
        print(f"Zero Trust Security Agent v1.0")
        print(f"=" * 60)
        print(f"User: {self.username}")
        print(f"Device ID: {self.device_id}")
        print(f"Backend: {BACKEND_URL}")
        print(f"Check Interval: {CHECK_INTERVAL}s")
        print(f"=" * 60)
        
        # Register device
        if not self.register_device():
            print("[WARN] Running in offline mode")
        
        print(f"\n[OK] Agent started. Monitoring activity...\n")
        
        cycle = 0
        while True:
            try:
                cycle += 1
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Cycle #{cycle}")
                
                # Collect data
                files = self.monitor_file_access()
                login_anomalies = self.check_login_anomalies()
                network_anomalies = self.check_network_anomalies()
                usb_anomalies = self.check_usb_devices()
                
                all_anomalies = login_anomalies + network_anomalies + usb_anomalies
                
                # Send to backend
                if files or all_anomalies:
                    self.send_telemetry(files, all_anomalies)
                else:
                    print("  No suspicious activity detected")
                
                # Wait for next cycle
                time.sleep(CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                print("\n[OK] Agent stopped by user")
                break
            except Exception as e:
                print(f"[ERROR] Monitoring error: {e}")
                time.sleep(60)

def main():
    if len(sys.argv) < 2:
        print("Usage: python zero_trust_agent.py <username>")
        print("Example: python zero_trust_agent.py bhargav")
        sys.exit(1)
    
    username = sys.argv[1]
    agent = ZeroTrustAgent(username)
    agent.run()

if __name__ == "__main__":
    main()
