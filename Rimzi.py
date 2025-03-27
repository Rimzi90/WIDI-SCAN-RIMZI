import subprocess
import platform
from typing import List, Tuple
import re

def get_os() -> str:
    """Check the operating system."""
    return platform.system()

def get_wifi_interface() -> str:
    """Detect the default WiFi interface."""
    if get_os() == "Linux":
        return "wlan0"
    elif get_os() == "Windows":
        return "Wi-Fi"
    elif get_os() == "Darwin":  # macOS
        return "en0"
    return "wlan0"  # Fallback

def scan_windows_wifi() -> List[Tuple[str, str, int]]:
    """
    Scan WiFi on Windows using `netsh` (no admin needed).
    Returns: List of (SSID, BSSID, Signal)
    """
    print("[+] Scanning WiFi on Windows (netsh)...")
    try:
        cmd = "netsh wlan show networks mode=Bssid"
        result = subprocess.check_output(cmd, shell=True, text=True)
        networks = []
        current_ssid = None
        
        for line in result.splitlines():
            if "SSID" in line and "BSSID" not in line:
                current_ssid = line.split(":")[1].strip()
            elif "BSSID" in line and current_ssid:
                bssid = line.split(":")[1].strip()
            elif "Signal" in line and current_ssid:
                signal = int(line.split(":")[1].replace("%", "").strip())
                networks.append((current_ssid, bssid, signal))
        return networks
    except Exception as e:
        print(f"[-] Windows scan error: {e}")
        return []

def scan_macos_wifi() -> List[Tuple[str, str, int]]:
    """
    Scan WiFi on macOS using `airport` (no sudo needed).
    Returns: List of (SSID, BSSID, Signal)
    """
    print("[+] Scanning WiFi on macOS (airport)...")
    try:
        cmd = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s"
        result = subprocess.check_output(cmd, shell=True, text=True)
        networks = []
        
        for line in result.splitlines()[1:]:  # Skip header
            parts = re.split(r'\s{2,}', line.strip())  # Split on multiple spaces
            if len(parts) >= 4:
                ssid = parts[0]
                bssid = parts[1]
                signal = int(parts[3].replace("%", ""))
                networks.append((ssid, bssid, signal))
        return networks
    except Exception as e:
        print(f"[-] macOS scan error: {e}")
        return []

def scan_linux_wifi() -> List[Tuple[str, str, int]]:
    """
    Scan WiFi on Linux using nmcli (no root needed).
    Returns: List of (SSID, BSSID, Signal)
    """
    print("[+] Scanning WiFi on Linux (nmcli)...")
    try:
        cmd = "nmcli -t -f SSID,BSSID,SIGNAL device wifi list"
        result = subprocess.check_output(cmd, shell=True, text=True)
        networks = []
        
        for line in result.splitlines():
            ssid, bssid, signal = line.split(":")
            networks.append((ssid, bssid, int(signal)))
        return networks
    except Exception as e:
        print(f"[-] Linux scan error: {e}")
        return []

def main():
    print("\n=== WiFi Scanner (No Root Needed) ===")
    print(f"OS: {get_os()}")
    
    networks = []
    if get_os() == "Windows":
        networks = scan_windows_wifi()
    elif get_os() == "Darwin":
        networks = scan_macos_wifi()
    elif get_os() == "Linux":
        networks = scan_linux_wifi()
    else:
        print("[-] Unsupported OS")
        return
    
    print(f"\n[+] Found {len(networks)} networks:")
    for i, (ssid, bssid, signal) in enumerate(networks, 1):
        print(f"{i}. SSID: {ssid or 'Hidden'}, BSSID: {bssid}, Signal: {signal}%")

if __name__ == "__main__":
    main()
