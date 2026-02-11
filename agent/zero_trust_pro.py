#!/usr/bin/env python3
"""
Zero Trust Security Agent - Professional Enterprise Edition
Modern UI with real-time monitoring and UEBA analytics
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
import webbrowser

BACKEND_URL = "https://zero-trust-3fmw.onrender.com"
CHECK_INTERVAL = 60

class ZeroTrustPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Zero Trust Security Monitor - Enterprise Edition")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0f1419')
        
        # Set icon (optional)
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        self.username = None
        self.monitoring = False
        self.stats = {
            'risk_score': 0,
            'threats': 0,
            'scans': 0,
            'files_monitored': 0
        }
        
        self.create_ui()
        
    def create_ui(self):
        # ===== TOP NAVIGATION BAR =====
        nav = tk.Frame(self.root, bg='#1a1f2e', height=80)
        nav.pack(fill='x')
        nav.pack_propagate(False)
        
        # Logo Section
        logo_frame = tk.Frame(nav, bg='#1a1f2e')
        logo_frame.pack(side='left', padx=30, pady=20)
        
        tk.Label(logo_frame, text="🛡️", font=('Segoe UI', 32), bg='#1a1f2e', fg='#00d9ff').pack(side='left')
        
        title_box = tk.Frame(logo_frame, bg='#1a1f2e')
        title_box.pack(side='left', padx=15)
        tk.Label(title_box, text="ZERO TRUST", font=('Segoe UI', 16, 'bold'), 
                bg='#1a1f2e', fg='#ffffff').pack(anchor='w')
        tk.Label(title_box, text="Enterprise Security Monitor", font=('Segoe UI', 9), 
                bg='#1a1f2e', fg='#00d9ff').pack(anchor='w')
        
        # Status Badge
        self.status_badge = tk.Frame(nav, bg='#ff4757', height=40, width=120)
        self.status_badge.pack(side='right', padx=30, pady=20)
        self.status_badge.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_badge, text="● OFFLINE", 
                                     font=('Segoe UI', 11, 'bold'),
                                     bg='#ff4757', fg='#ffffff')
        self.status_label.pack(expand=True)
        
        # ===== MAIN CONTENT AREA =====
        content = tk.Frame(self.root, bg='#0f1419')
        content.pack(fill='both', expand=True)
        
        # ===== LOGIN SCREEN =====
        self.login_screen = tk.Frame(content, bg='#0f1419')
        self.login_screen.pack(fill='both', expand=True)
        
        login_center = tk.Frame(self.login_screen, bg='#0f1419')
        login_center.place(relx=0.5, rely=0.5, anchor='center')
        
        # Login Card
        login_card = tk.Frame(login_center, bg='#1a1f2e', relief='flat')
        login_card.pack(padx=50, pady=50)
        
        # Icon
        tk.Label(login_card, text="🔐", font=('Segoe UI', 48), bg='#1a1f2e').pack(pady=(40,20))
        
        tk.Label(login_card, text="SECURE ACCESS", font=('Segoe UI', 20, 'bold'),
                bg='#1a1f2e', fg='#00d9ff').pack(pady=10)
        
        tk.Label(login_card, text="Enter your credentials to start monitoring", 
                font=('Segoe UI', 10), bg='#1a1f2e', fg='#8b92a8').pack(pady=5)
        
        # Username Input
        input_frame = tk.Frame(login_card, bg='#1a1f2e')
        input_frame.pack(pady=30, padx=60)
        
        tk.Label(input_frame, text="Username", font=('Segoe UI', 10, 'bold'),
                bg='#1a1f2e', fg='#ffffff').pack(anchor='w', pady=(0,8))
        
        self.username_entry = tk.Entry(input_frame, font=('Segoe UI', 13), width=28,
                                      bg='#0f1419', fg='#ffffff', 
                                      insertbackground='#00d9ff', relief='flat', bd=0)
        self.username_entry.pack(ipady=12, fill='x')
        self.username_entry.bind('<Return>', lambda e: self.start_monitoring())
        
        # Underline
        tk.Frame(input_frame, bg='#00d9ff', height=2).pack(fill='x')
        
        # Start Button
        start_btn = tk.Button(login_card, text="START MONITORING",
                             command=self.start_monitoring,
                             font=('Segoe UI', 12, 'bold'),
                             bg='#00d9ff', fg='#000000',
                             activebackground='#00b8d4',
                             relief='flat', cursor='hand2',
                             width=25, height=2)
        start_btn.pack(pady=(20,40))
        
        # ===== DASHBOARD SCREEN =====
        self.dashboard = tk.Frame(content, bg='#0f1419')
        
        # Dashboard Content
        dash_content = tk.Frame(self.dashboard, bg='#0f1419')
        dash_content.pack(fill='both', expand=True, padx=30, pady=20)
        
        # ===== STATS CARDS ROW =====
        stats_row = tk.Frame(dash_content, bg='#0f1419')
        stats_row.pack(fill='x', pady=(0,20))
        
        self.create_stat_card(stats_row, "RISK SCORE", "0", "#ff4757", "⚠️", 0)
        self.create_stat_card(stats_row, "THREATS", "0", "#ffa502", "🚨", 1)
        self.create_stat_card(stats_row, "SCANS", "0", "#00d9ff", "🔍", 2)
        self.create_stat_card(stats_row, "FILES", "0", "#2ed573", "📁", 3)
        
        # ===== MAIN PANELS =====
        panels = tk.Frame(dash_content, bg='#0f1419')
        panels.pack(fill='both', expand=True)
        
        # LEFT PANEL
        left = tk.Frame(panels, bg='#0f1419', width=380)
        left.pack(side='left', fill='both', padx=(0,15))
        left.pack_propagate(False)
        
        # Device Info Card
        device_card = self.create_panel(left, "DEVICE INFORMATION", "💻")
        device_card.pack(fill='x', pady=(0,15))
        
        self.device_text = tk.Text(device_card, height=9, font=('Consolas', 9),
                                  bg='#0f1419', fg='#00d9ff', bd=0, wrap='word',
                                  relief='flat')
        self.device_text.pack(padx=20, pady=15, fill='x')
        
        # Security Status Card
        status_card = self.create_panel(left, "SECURITY STATUS", "🔒")
        status_card.pack(fill='x', pady=(0,15))
        
        status_items = [
            ("Real-time Monitoring", "✓", "#2ed573"),
            ("File Access Tracking", "✓", "#2ed573"),
            ("Network Analysis", "✓", "#2ed573"),
            ("USB Detection", "✓", "#2ed573"),
            ("Geolocation Tracking", "✓", "#2ed573"),
            ("UEBA Risk Scoring", "✓", "#2ed573")
        ]
        
        for item, icon, color in status_items:
            row = tk.Frame(status_card, bg='#1a1f2e')
            row.pack(fill='x', padx=20, pady=3)
            tk.Label(row, text=icon, font=('Segoe UI', 10, 'bold'),
                    bg='#1a1f2e', fg=color, width=3).pack(side='left')
            tk.Label(row, text=item, font=('Segoe UI', 9),
                    bg='#1a1f2e', fg='#ffffff', anchor='w').pack(side='left', fill='x')
        
        tk.Label(status_card, text="", bg='#1a1f2e').pack(pady=8)
        
        # Control Buttons
        controls = self.create_panel(left, "CONTROLS", "⚙️")
        controls.pack(fill='x')
        
        btn_container = tk.Frame(controls, bg='#1a1f2e')
        btn_container.pack(pady=20, padx=20)
        
        self.create_button(btn_container, "📊 OPEN DASHBOARD", self.open_dashboard, 
                          "#00d9ff", "#000000").pack(pady=5, fill='x')
        self.create_button(btn_container, "🔄 MANUAL SCAN", self.manual_scan,
                          "#2ed573", "#000000").pack(pady=5, fill='x')
        self.create_button(btn_container, "📈 VIEW ANALYTICS", self.view_analytics,
                          "#5f27cd", "#ffffff").pack(pady=5, fill='x')
        self.create_button(btn_container, "🔗 BLOCKCHAIN AUDIT", self.view_blockchain,
                          "#ff9f43", "#000000").pack(pady=5, fill='x')
        self.create_button(btn_container, "🛡️ SECURITY ZONES", self.view_zones,
                          "#00d2d3", "#000000").pack(pady=5, fill='x')
        self.create_button(btn_container, "⛔ STOP MONITORING", self.stop_monitoring,
                          "#ff4757", "#ffffff").pack(pady=5, fill='x')
        
        # RIGHT PANEL
        right = tk.Frame(panels, bg='#0f1419')
        right.pack(side='right', fill='both', expand=True)
        
        # Activity Log
        log_card = self.create_panel(right, "ACTIVITY LOG", "📋")
        log_card.pack(fill='both', expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_card, font=('Consolas', 9),
                                                  bg='#0f1419', fg='#ffffff',
                                                  wrap='word', bd=0, relief='flat')
        self.log_text.pack(padx=20, pady=15, fill='both', expand=True)
        
        # Configure tags
        self.log_text.tag_config('info', foreground='#00d9ff')
        self.log_text.tag_config('success', foreground='#2ed573')
        self.log_text.tag_config('warning', foreground='#ffa502')
        self.log_text.tag_config('error', foreground='#ff4757')
        self.log_text.tag_config('time', foreground='#8b92a8')
        
    def create_panel(self, parent, title, icon):
        panel = tk.Frame(parent, bg='#1a1f2e', relief='flat')
        
        header = tk.Frame(panel, bg='#1a1f2e')
        header.pack(fill='x', padx=20, pady=(20,10))
        
        tk.Label(header, text=icon, font=('Segoe UI', 14), bg='#1a1f2e').pack(side='left', padx=(0,10))
        tk.Label(header, text=title, font=('Segoe UI', 11, 'bold'),
                bg='#1a1f2e', fg='#ffffff').pack(side='left')
        
        tk.Frame(panel, bg='#00d9ff', height=2).pack(fill='x', padx=20)
        
        return panel
    
    def create_stat_card(self, parent, label, value, color, icon, col):
        card = tk.Frame(parent, bg='#1a1f2e', relief='flat')
        card.grid(row=0, column=col, padx=8, sticky='ew')
        parent.grid_columnconfigure(col, weight=1)
        
        tk.Label(card, text=icon, font=('Segoe UI', 24), bg='#1a1f2e').pack(pady=(20,5))
        
        value_label = tk.Label(card, text=value, font=('Segoe UI', 28, 'bold'),
                              bg='#1a1f2e', fg=color)
        value_label.pack()
        
        tk.Label(card, text=label, font=('Segoe UI', 9),
                bg='#1a1f2e', fg='#8b92a8').pack(pady=(5,20))
        
        if col == 0:
            self.risk_label = value_label
        elif col == 1:
            self.threat_label = value_label
        elif col == 2:
            self.scan_label = value_label
        elif col == 3:
            self.file_label = value_label
    
    def create_button(self, parent, text, command, bg, fg):
        btn = tk.Button(parent, text=text, command=command,
                       font=('Segoe UI', 10, 'bold'),
                       bg=bg, fg=fg, activebackground=bg,
                       relief='flat', cursor='hand2',
                       width=22, height=2)
        return btn
    
    def log(self, message, tag='info'):
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert('end', f"[{timestamp}] ", 'time')
        self.log_text.insert('end', f"{message}\n", tag)
        self.log_text.see('end')
        self.root.update()
    
    def start_monitoring(self):
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter your username!")
            return
        
        self.username = username
        self.login_screen.pack_forget()
        self.dashboard.pack(fill='both', expand=True)
        
        self.status_badge.config(bg='#2ed573')
        self.status_label.config(text='● ONLINE', bg='#2ed573')
        
        self.update_device_info()
        self.log("🚀 Zero Trust Agent initialized successfully", 'success')
        self.log(f"👤 Monitoring user: {username}", 'info')
        self.log(f"🔗 Connected to: {BACKEND_URL}", 'info')
        
        self.monitoring = True
        threading.Thread(target=self.monitor_loop, daemon=True).start()
    
    def stop_monitoring(self):
        self.monitoring = False
        self.status_badge.config(bg='#ff4757')
        self.status_label.config(text='● OFFLINE', bg='#ff4757')
        self.log("⛔ Monitoring stopped by user", 'warning')
    
    def open_dashboard(self):
        webbrowser.open('https://zer0-trust.netlify.app')
        self.log("🌐 Opening web dashboard...", 'info')
    
    def view_analytics(self):
        """Show detailed analytics window"""
        analytics_win = tk.Toplevel(self.root)
        analytics_win.title("Security Analytics")
        analytics_win.geometry("800x600")
        analytics_win.configure(bg='#0f1419')
        
        tk.Label(analytics_win, text="📊 SECURITY ANALYTICS", 
                font=('Segoe UI', 18, 'bold'), bg='#0f1419', fg='#00d9ff').pack(pady=20)
        
        # Stats Frame
        stats_frame = tk.Frame(analytics_win, bg='#1a1f2e')
        stats_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        stats_text = f"""
╔══════════════════════════════════════════════════════════╗
║                  SECURITY METRICS                        ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  Current Risk Score:        {self.stats['risk_score']}/100                        ║
║  Total Threats Detected:    {self.stats['threats']}                              ║
║  Security Scans Performed:  {self.stats['scans']}                              ║
║  Files Monitored:           {self.stats['files_monitored']}                              ║
║                                                          ║
║  Risk Level:                {'CRITICAL' if self.stats['risk_score'] > 70 else 'HIGH' if self.stats['risk_score'] > 50 else 'MEDIUM' if self.stats['risk_score'] > 30 else 'LOW'}                           ║
║  Access Decision:           {'DENY' if self.stats['risk_score'] > 70 else 'RESTRICT' if self.stats['risk_score'] > 30 else 'ALLOW'}                          ║
║  Access Zone:               {'PUBLIC' if self.stats['risk_score'] > 70 else 'INTERNAL' if self.stats['risk_score'] > 50 else 'SENSITIVE' if self.stats['risk_score'] > 30 else 'CRITICAL'}                        ║
║                                                          ║
║  System Status:             {'⚠️ ALERT' if self.stats['risk_score'] > 50 else '✓ SECURE'}                         ║
║  Monitoring Status:         {'● ACTIVE' if self.monitoring else '○ INACTIVE'}                        ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

RECOMMENDATIONS:
{'• Immediate action required - High risk detected!' if self.stats['risk_score'] > 70 else '• Review security logs regularly' if self.stats['risk_score'] > 30 else '• System operating normally'}
{'• Contact security team' if self.stats['risk_score'] > 70 else '• Monitor suspicious activities' if self.stats['risk_score'] > 30 else '• Continue monitoring'}
{'• Consider access restrictions' if self.stats['risk_score'] > 50 else '• Maintain current security posture'}
        """
        
        text_widget = tk.Text(stats_frame, font=('Consolas', 10), bg='#0f1419', 
                             fg='#00d9ff', wrap='word', relief='flat')
        text_widget.pack(fill='both', expand=True, padx=20, pady=20)
        text_widget.insert('1.0', stats_text)
        text_widget.config(state='disabled')
        
        tk.Button(analytics_win, text="CLOSE", command=analytics_win.destroy,
                 font=('Segoe UI', 10, 'bold'), bg='#ff4757', fg='#ffffff',
                 relief='flat', cursor='hand2', width=15, height=2).pack(pady=20)
        
        self.log("📊 Analytics window opened", 'info')
    
    def view_blockchain(self):
        """Show blockchain audit trail"""
        blockchain_win = tk.Toplevel(self.root)
        blockchain_win.title("Blockchain Audit Trail")
        blockchain_win.geometry("900x600")
        blockchain_win.configure(bg='#0f1419')
        
        tk.Label(blockchain_win, text="🔗 BLOCKCHAIN AUDIT TRAIL", 
                font=('Segoe UI', 18, 'bold'), bg='#0f1419', fg='#ff9f43').pack(pady=20)
        
        # Fetch blockchain data
        try:
            response = requests.get(f"{BACKEND_URL}/audit/chain", timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                info_frame = tk.Frame(blockchain_win, bg='#1a1f2e')
                info_frame.pack(fill='x', padx=30, pady=10)
                
                tk.Label(info_frame, text=f"Chain Length: {data.get('chain_length', 0)} blocks",
                        font=('Segoe UI', 11), bg='#1a1f2e', fg='#ffffff').pack(pady=5)
                tk.Label(info_frame, text=f"Status: {'✓ Valid' if data.get('is_valid') else '✗ Invalid'}",
                        font=('Segoe UI', 11), bg='#1a1f2e', 
                        fg='#2ed573' if data.get('is_valid') else '#ff4757').pack(pady=5)
                
                # Blocks display
                blocks_frame = tk.Frame(blockchain_win, bg='#1a1f2e')
                blocks_frame.pack(fill='both', expand=True, padx=30, pady=10)
                
                text_widget = scrolledtext.ScrolledText(blocks_frame, font=('Consolas', 9),
                                                        bg='#0f1419', fg='#ff9f43',
                                                        wrap='word', relief='flat')
                text_widget.pack(fill='both', expand=True, padx=20, pady=20)
                
                blocks = data.get('blocks', [])
                for block in blocks:
                    text_widget.insert('end', f"\n{'='*70}\n")
                    text_widget.insert('end', f"Block #{block.get('index', 0)}\n")
                    text_widget.insert('end', f"Timestamp: {block.get('timestamp', 'N/A')}\n")
                    text_widget.insert('end', f"Previous Hash: {block.get('previous_hash', 'N/A')[:32]}...\n")
                    text_widget.insert('end', f"Transactions: {len(block.get('data', []))}\n")
                    
                    for tx in block.get('data', []):
                        text_widget.insert('end', f"  • {tx.get('type', 'N/A')}: {tx.get('user', 'N/A')} - {tx.get('timestamp', 'N/A')}\n")
                
                text_widget.config(state='disabled')
            else:
                tk.Label(blockchain_win, text="Failed to fetch blockchain data",
                        font=('Segoe UI', 12), bg='#0f1419', fg='#ff4757').pack(pady=50)
        except Exception as e:
            tk.Label(blockchain_win, text=f"Error: {str(e)}",
                    font=('Segoe UI', 12), bg='#0f1419', fg='#ff4757').pack(pady=50)
        
        tk.Button(blockchain_win, text="CLOSE", command=blockchain_win.destroy,
                 font=('Segoe UI', 10, 'bold'), bg='#ff4757', fg='#ffffff',
                 relief='flat', cursor='hand2', width=15, height=2).pack(pady=20)
        
        self.log("🔗 Blockchain audit trail opened", 'info')
    
    def view_zones(self):
        """Show micro-segmentation zones"""
        zones_win = tk.Toplevel(self.root)
        zones_win.title("Security Zones - Micro-Segmentation")
        zones_win.geometry("1000x700")
        zones_win.configure(bg='#0f1419')
        
        tk.Label(zones_win, text="🛡️ MICRO-SEGMENTATION ZONES", 
                font=('Segoe UI', 18, 'bold'), bg='#0f1419', fg='#00d2d3').pack(pady=20)
        
        # Fetch zones data
        try:
            response = requests.get(f"{BACKEND_URL}/zones", timeout=5)
            if response.status_code == 200:
                data = response.json()
                zones = data.get('zones', [])
                
                # Current user zone
                current_zone = 'CRITICAL' if self.stats['risk_score'] <= 30 else 'SENSITIVE' if self.stats['risk_score'] <= 50 else 'INTERNAL' if self.stats['risk_score'] <= 70 else 'PUBLIC'
                
                tk.Label(zones_win, text=f"Your Current Access Zone: {current_zone}",
                        font=('Segoe UI', 12, 'bold'), bg='#0f1419', 
                        fg='#2ed573' if current_zone == 'CRITICAL' else '#ffa502').pack(pady=10)
                
                # Zones display
                zones_frame = tk.Frame(zones_win, bg='#0f1419')
                zones_frame.pack(fill='both', expand=True, padx=30, pady=20)
                
                for i, zone in enumerate(zones):
                    zone_card = tk.Frame(zones_frame, bg='#1a1f2e', relief='flat')
                    zone_card.pack(fill='x', pady=10)
                    
                    # Header
                    header = tk.Frame(zone_card, bg='#1a1f2e')
                    header.pack(fill='x', padx=20, pady=15)
                    
                    color = '#2ed573' if zone['name'] == 'CRITICAL' else '#00d9ff' if zone['name'] == 'SENSITIVE' else '#ffa502' if zone['name'] == 'INTERNAL' else '#ff4757'
                    
                    tk.Label(header, text=f"{'🔒' if zone['name'] == 'CRITICAL' else '🔐' if zone['name'] == 'SENSITIVE' else '🔓' if zone['name'] == 'INTERNAL' else '🌐'}",
                            font=('Segoe UI', 20), bg='#1a1f2e').pack(side='left', padx=(0,15))
                    
                    info = tk.Frame(header, bg='#1a1f2e')
                    info.pack(side='left', fill='x', expand=True)
                    
                    tk.Label(info, text=zone['name'], font=('Segoe UI', 14, 'bold'),
                            bg='#1a1f2e', fg=color).pack(anchor='w')
                    tk.Label(info, text=zone['description'], font=('Segoe UI', 9),
                            bg='#1a1f2e', fg='#8b92a8').pack(anchor='w')
                    
                    # Access indicator
                    if zone['name'] == current_zone or (zone['risk_threshold'] >= self.stats['risk_score']):
                        tk.Label(header, text="✓ ACCESSIBLE", font=('Segoe UI', 10, 'bold'),
                                bg='#2ed573', fg='#ffffff', padx=15, pady=5).pack(side='right')
                    else:
                        tk.Label(header, text="✗ RESTRICTED", font=('Segoe UI', 10, 'bold'),
                                bg='#ff4757', fg='#ffffff', padx=15, pady=5).pack(side='right')
                    
                    # Resources
                    tk.Label(zone_card, text=f"Risk Threshold: ≤{zone['risk_threshold']}",
                            font=('Segoe UI', 9), bg='#1a1f2e', fg='#8b92a8').pack(anchor='w', padx=20)
                    
                    tk.Label(zone_card, text="Resources:", font=('Segoe UI', 9, 'bold'),
                            bg='#1a1f2e', fg='#ffffff').pack(anchor='w', padx=20, pady=(10,5))
                    
                    for resource in zone['resources']:
                        tk.Label(zone_card, text=f"  • {resource}", font=('Segoe UI', 9),
                                bg='#1a1f2e', fg='#ffffff').pack(anchor='w', padx=20)
                    
                    tk.Label(zone_card, text="", bg='#1a1f2e').pack(pady=5)
            else:
                tk.Label(zones_win, text="Failed to fetch zones data",
                        font=('Segoe UI', 12), bg='#0f1419', fg='#ff4757').pack(pady=50)
        except Exception as e:
            tk.Label(zones_win, text=f"Error: {str(e)}",
                    font=('Segoe UI', 12), bg='#0f1419', fg='#ff4757').pack(pady=50)
        
        tk.Button(zones_win, text="CLOSE", command=zones_win.destroy,
                 font=('Segoe UI', 10, 'bold'), bg='#ff4757', fg='#ffffff',
                 relief='flat', cursor='hand2', width=15, height=2).pack(pady=20)
        
        self.log("🛡️ Security zones window opened", 'info')
    
    def manual_scan(self):
        self.log("🔄 Manual security scan initiated...", 'info')
        threading.Thread(target=self.perform_scan, daemon=True).start()
    
    def update_device_info(self):
        hostname = socket.gethostname()
        os_info = f"{platform.system()} {platform.release()}"
        ip = socket.gethostbyname(hostname)
        device_id = hashlib.sha256(f"{uuid.getnode()}-{hostname}".encode()).hexdigest()[:16]
        
        info = f"""
User:       {self.username}
Hostname:   {hostname}
OS:         {os_info}
IP Address: {ip}
Device ID:  {device_id}
Status:     Connected
Backend:    Active
        """
        self.device_text.delete('1.0', 'end')
        self.device_text.insert('1.0', info.strip())
    
    def perform_scan(self):
        self.stats['scans'] += 1
        self.scan_label.config(text=str(self.stats['scans']))
        
        threats = []
        
        # Check time
        hour = datetime.now().hour
        if hour < 8 or hour > 18:
            threats.append(("⚠️ Odd-hour access detected", 'warning', 10))
        
        # Check weekend
        if datetime.now().weekday() >= 5:
            threats.append(("⚠️ Weekend access detected", 'warning', 5))
        
        # Check network
        try:
            connections = psutil.net_connections(kind='inet')
            external = sum(1 for c in connections if c.raddr and c.status == 'ESTABLISHED' 
                          and not c.raddr.ip.startswith(('10.', '192.168.', '172.')))
            if external > 10:
                threats.append((f"🌐 {external} external connections detected", 'warning', 15))
        except:
            pass
        
        # Check USB
        try:
            for partition in psutil.disk_partitions():
                if 'removable' in partition.opts.lower():
                    threats.append(("💾 USB device connected", 'error', 20))
                    break
        except:
            pass
        
        # Check resources
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        if cpu > 80:
            threats.append((f"⚡ High CPU usage: {cpu}%", 'warning', 5))
        if mem > 80:
            threats.append((f"💾 High memory usage: {mem}%", 'warning', 5))
        
        # Update stats
        if threats:
            self.stats['threats'] += len(threats)
            self.threat_label.config(text=str(self.stats['threats']))
            
            for msg, tag, risk in threats:
                self.log(msg, tag)
                self.stats['risk_score'] += risk
            
            self.risk_label.config(text=str(min(self.stats['risk_score'], 100)))
        else:
            self.log("✓ No threats detected - System secure", 'success')
        
        self.stats['files_monitored'] += 1
        self.file_label.config(text=str(self.stats['files_monitored']))
    
    def monitor_loop(self):
        # Register device
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
            device_info = {
                "username": self.username,
                "device_id": hashlib.sha256(f"{uuid.getnode()}".encode()).hexdigest()[:16],
                "mac_address": mac,
                "hostname": socket.gethostname(),
                "os": f"{platform.system()} {platform.release()}",
                "wifi_ssid": "Unknown",
                "ip_address": socket.gethostbyname(socket.gethostname())
            }
            requests.post(f"{BACKEND_URL}/device/register", json=device_info, timeout=10)
            self.log("✓ Device registered with backend", 'success')
        except:
            self.log("⚠️ Running in offline mode", 'warning')
        
        while self.monitoring:
            self.perform_scan()
            for _ in range(CHECK_INTERVAL):
                if not self.monitoring:
                    break
                time.sleep(1)

def main():
    root = tk.Tk()
    app = ZeroTrustPro(root)
    root.mainloop()

if __name__ == "__main__":
    main()
