from collections import defaultdict
from datetime import datetime, timedelta

def analyze_ueba(login_logs, device_logs, file_logs):
    ueba = defaultdict(set)
    login_count = defaultdict(int)
    login_ips = defaultdict(set)
    login_countries = defaultdict(set)

    for log in login_logs:
        user = log["user_id"]
        login_count[user] += 1

        hour = log["login_time"].hour
        if hour < 6 or hour > 22:
            ueba[user].add("ODD_LOGIN_TIME")

        if not log["success"]:
            ueba[user].add("FAILED_LOGIN")

        ip = log.get("ip_address", "")
        login_ips[user].add(ip)
        
        if ip and not ip.startswith(("10.", "192.", "172.")):
            ueba[user].add("EXTERNAL_NETWORK")

        country = log.get("country", "Unknown")
        login_countries[user].add(country)

    for user, count in login_count.items():
        if count > 5:
            ueba[user].add("MULTIPLE_LOGIN_ATTEMPTS")

    for user, countries in login_countries.items():
        if len(countries) > 2:
            ueba[user].add("GEOLOCATION_ANOMALY")

    for user, ips in login_ips.items():
        if len(ips) > 3:
            ueba[user].add("MULTIPLE_IP_ADDRESSES")

    device_map = defaultdict(set)
    for dev in device_logs:
        user = dev["user_id"]
        mac = dev.get("mac_address")
        device_map[user].add(mac)

        if mac == "UNKNOWN":
            ueba[user].add("UNKNOWN_DEVICE_ID")

        if dev.get("wifi_ssid", "").lower() in ["iphone", "android", "hotspot"]:
            ueba[user].add("HOTSPOT_NETWORK")

        if not dev.get("trusted", False):
            ueba[user].add("UNTRUSTED_DEVICE")

    for user, devices in device_map.items():
        if len(devices) > 2:
            ueba[user].add("DEVICE_CHANGE_DETECTED")

    sensitive = ["credentials.txt", "secrets.env", ".env", "id_rsa", "config.json"]
    file_access_count = defaultdict(int)
    
    for f in file_logs:
        user = f["user_id"]
        file_access_count[user] += 1
        
        if f["file_name"] in sensitive:
            ueba[user].add("SENSITIVE_FILE_ACCESS")
        
        if f.get("action") == "DELETE":
            ueba[user].add("FILE_DELETION")

    for user, count in file_access_count.items():
        if count > 20:
            ueba[user].add("EXCESSIVE_FILE_ACCESS")

    return {u: list(s) for u, s in ueba.items()}
