#!/usr/bin/env python3
"""
Zero Trust Security Agent - GUI Version
Professional security monitoring tool with graphical interface
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import socket
import platform
import uuid
import hashlib
import requests
import psutil
from datetime import datetime
import time

BACKEND_URL = "https://zero-trust-3fmw.onrender.com"
CHECK_INTERVAL = 300

class ZeroTrustGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Zero Trust Security Agent v1.0")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a1a')
        
        self.username = None
        self.device_id = None
        self.monitoring = False
        self.agent_thread = None
        
        self.create_widgets()
        
    def create_widgets(self):
        # Header
        header = tk.Frame(self.root, bg='#0d0d0d', height=80)
        header.pack(fill='x', padx=0, pady=0)
        
        title = tk.Label(header, text="🛡️ ZERO TRUST SECURITY AGENT", 
                        font=('Courier New', 20, 'bold'), 
                        bg='#0d0d0d', fg='#00ff00')
        title.pack(pady=20)
        
        # Main container
        main = tk.Frame(self.root, bg='#1a1a1a')
        main.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Login Section
        self.login_frame = tk.Frame(main, bg='#1a1a1a')
        self.login_frame.pack(pady=50)
        
        tk.Label(self.login_frame, text="Enter Username:", 
                font=('Courier New', 12), bg='#1a1a1a', fg='#00ff00').pack(pady=10)
        
        self.username_entry = tk.Entry(self.login_frame, font=('Courier New', 14), 
                                      width=30, bg='#0d0d0d', fg='#00ff00', 
                                      insertbackground='#00ff00')
        self.username_entry.pack(pady=10)
        self.username_entry.bind('<Return>', lambda e: self.start_monitoring())
        
        self.start_btn = tk.Button(self.login_frame, text="START MONITORING", 
                                   command=self.start_monitoring,
                                   font=('Courier New', 12, 'bold'),
                                   bg='#00ff00', fg='#000000', 
                                   activebackground='#00cc00',
                                   width=20, height=2)
        self.start_btn.pack(pady=20)
        
        # Monitoring Section (hidden initially)
        self.monitor_frame = tk.Frame(main, bg='#1a1a1a')
        
        # Status Panel
        status_frame = tk.Frame(self.monitor_frame, bg='#0d0d0d', relief='solid', bd=2)
        status_frame.pack(fill='x', pady=10)
        
        self.status_label = tk.Label(status_frame, text="● OFFLINE", 
                                     font=('Courier New', 14, 'bold'),
                                     bg='#0d0d0d', fg='#ff0000')
        self.status_label.pack(pady=10)
        
        # Info Panel
        info_frame = tk.LabelFrame(self.monitor_frame, text="DEVICE INFO", 
                                  font=('Courier New', 10, 'bold'),
                                  bg='#1a1a1a', fg='#00ff00', bd=2)
        info_frame.pack(fill='x', pady=10)
        
        self.info_text = tk.Text(info_frame, height=6, font=('Courier New', 9),
                                bg='#0d0d0d', fg='#00ff00', bd=0)
        self.info_text.pack(padx=10, pady=10, fill='x')
        
        # Activity Log
        log_frame = tk.LabelFrame(self.monitor_frame, text="ACTIVITY LOG", 
                                 font=('Courier New', 10, 'bold'),
                                 bg='#1a1a1a', fg='#00ff00', bd=2)
        log_frame.pack(fill='both', expand=True, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, 
                                                  font=('Courier New', 9),
                                                  bg='#0d0d0d', fg='#00ff00',
                                                  wrap='word')
        self.log_text.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Control Buttons
        btn_frame = tk.Frame(self.monitor_frame, bg='#1a1a1a')
        btn_frame.pack(fill='x', pady=10)
        
        self.stop_btn = tk.Button(btn_frame, text="STOP MONITORING", 
                                  command=self.stop_monitoring,
                                  font=('Courier New', 10, 'bold'),
                                  bg='#ff0000', fg='#ffffff',
                                  width=20, height=2)
        self.stop_btn.pack(side='left', padx=5)
        
        self.dashboard_btn = tk.Button(btn_frame, text="OPEN DASHBOARD", 
                                      command=self.open_dashboard,
                                      font=('Courier New', 10, 'bold'),
                                      bg='#0000ff', fg='#ffffff',
                                      width=20, height=2)
        self.dashboard_btn.pack(side='left', padx=5)
        
    def log(self, message, color='#00ff00'):
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert('end', f"[{timestamp}] {message}\n")
        self.log_text.see('end')
        self.root.update()
        
    def start_monitoring(self):
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter a username!")
            return
        
        self.username = username
        self.device_id = self.get_device_id()
        
        # Hide login, show monitoring
        self.login_frame.pack_forget()
        self.monitor_frame.pack(fill='both', expand=True)
        
        # Update device info
        self.update_device_info()
        
        # Start monitoring thread
        self.monitoring = True
        self.agent_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.agent_thread.start()
        
        self.status_label.config(text="● ONLINE", fg='#00ff00')
        self.log("Agent started successfully", '#00ff00')
        
    def stop_monitoring(self):
        self.monitoring = False
        self.status_label.config(text="● OFFLINE", fg='#ff0000')
        self.log("Agent stopped by user", '#ffff00')
        
    def open_dashboard(self):
        import webbrowser
        webbrowser.open('https://zer0-trust.netlify.app')
        self.log("Opening dashboard in browser...", '#00ffff')
        
    def get_device_id(self):
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
        hostname = socket.gethostname()
        return hashlib.sha256(f"{mac}-{hostname}".encode()).hexdigest()[:16]
    
    def update_device_info(self):
        hostname = socket.gethostname()
        os_info = f"{platform.system()} {platform.release()}"
        ip = socket.gethostbyname(hostname)
        
        info = f"""
User:      {self.username}
Device ID: {self.device_id}
Hostname:  {hostname}
OS:        {os_info}
IP:        {ip}
Backend:   {BACKEND_URL}
        """
        self.info_text.delete('1.0', 'end')
        self.info_text.insert('1.0', info)
        
    def register_device(self):
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
            hostname = socket.gethostname()
            os_info = f"{platform.system()} {platform.release()}"
            ip = socket.gethostbyname(hostname)
            
            device_info = {
                "username": self.username,
                "device_id": self.device_id,
                "mac_address": mac,
                "hostname": hostname,
                "os": os_info,
                "wifi_ssid": "Unknown",
                "ip_address": ip
            }
            
            response = requests.post(f"{BACKEND_URL}/device/register", 
                                    json=device_info, timeout=10)
            
            if response.status_code == 200:
                self.log(f"Device registered: {hostname}", '#00ff00')
                return True
            else:
                self.log(f"Registration failed: {response.status_code}", '#ff0000')
                return False
        except Exception as e:
            self.log(f"Cannot connect to backend: {e}", '#ff0000')
            return False
    
    def monitor_loop(self):
        # Register device
        self.register_device()
        
        cycle = 0
        while self.monitoring:
            try:
                cycle += 1
                self.log(f"Cycle #{cycle} - Scanning...", '#00ffff')
                
                # Check for anomalies
                anomalies = []
                
                # Check login time
                hour = datetime.now().hour
                if hour < 8 or hour > 18:
                    anomalies.append("ODD_HOUR_ACCESS")
                
                # Check weekend
                if datetime.now().weekday() >= 5:
                    anomalies.append("WEEKEND_ACCESS")
                
                # Check network connections
                try:
                    connections = psutil.net_connections(kind='inet')
                    external_ips = set()
                    for conn in connections:
                        if conn.raddr and conn.status == 'ESTABLISHED':
                            remote_ip = conn.raddr.ip
                            if not (remote_ip.startswith('10.') or 
                                   remote_ip.startswith('192.168.') or 
                                   remote_ip.startswith('172.')):
                                external_ips.add(remote_ip)
                    
                    if len(external_ips) > 10:
                        anomalies.append("EXCESSIVE_EXTERNAL_CONNECTIONS")
                except:
                    pass
                
                # Check USB devices
                try:
                    partitions = psutil.disk_partitions()
                    for partition in partitions:
                        if 'removable' in partition.opts.lower():
                            anomalies.append("USB_DEVICE_DETECTED")
                            break
                except:
                    pass
                
                if anomalies:
                    self.log(f"⚠️ ALERTS: {', '.join(anomalies)}", '#ff0000')
                else:
                    self.log("✓ No suspicious activity detected", '#00ff00')
                
                # Wait for next cycle
                for _ in range(CHECK_INTERVAL):
                    if not self.monitoring:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.log(f"Error: {e}", '#ff0000')
                time.sleep(60)

def main():
    root = tk.Tk()
    app = ZeroTrustGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
