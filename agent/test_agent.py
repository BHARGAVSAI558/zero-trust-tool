#!/usr/bin/env python3
"""
Test script to simulate employee activity and verify agent monitoring
"""

import os
import time
from pathlib import Path

def simulate_file_access():
    """Simulate accessing sensitive files"""
    print("\n[TEST] Simulating file access...")
    
    # Create test directories
    test_dirs = ["Documents/confidential", "Desktop/payroll", "Downloads/secret"]
    
    for dir_path in test_dirs:
        full_path = Path.home() / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        
        # Create and access test file
        test_file = full_path / "test_data.txt"
        test_file.write_text("Sensitive information")
        
        # Read file (triggers monitoring)
        content = test_file.read_text()
        print(f"  ✓ Accessed: {test_file}")
    
    print("[OK] File access simulation complete")

def simulate_network_activity():
    """Simulate network connections"""
    print("\n[TEST] Simulating network activity...")
    
    import socket
    external_hosts = [
        ("google.com", 80),
        ("github.com", 443),
        ("amazon.com", 443)
    ]
    
    for host, port in external_hosts:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((host, port))
            sock.close()
            print(f"  ✓ Connected to: {host}:{port}")
        except:
            print(f"  ✗ Failed to connect: {host}:{port}")
    
    print("[OK] Network simulation complete")

def check_agent_status():
    """Check if agent is running"""
    print("\n[TEST] Checking agent status...")
    
    import psutil
    agent_running = False
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and 'zero_trust_agent.py' in ' '.join(proc.info['cmdline']):
                agent_running = True
                print(f"  ✓ Agent running (PID: {proc.info['pid']})")
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if not agent_running:
        print("  ✗ Agent not running!")
        print("  Start agent: python zero_trust_agent.py <username>")
    
    return agent_running

def main():
    print("=" * 60)
    print("Zero Trust Agent - Test Suite")
    print("=" * 60)
    
    # Check if agent is running
    agent_running = check_agent_status()
    
    if not agent_running:
        print("\n[WARN] Agent must be running to see monitoring in action")
        print("Run in another terminal: python zero_trust_agent.py testuser")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Run simulations
    simulate_file_access()
    time.sleep(2)
    simulate_network_activity()
    
    print("\n" + "=" * 60)
    print("[OK] Test complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Check agent console for detected activity")
    print("2. View admin dashboard: https://zer0-trust.netlify.app")
    print("3. Verify file access logs in database")
    print("=" * 60)

if __name__ == "__main__":
    main()
