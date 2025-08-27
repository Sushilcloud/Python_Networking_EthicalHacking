# connected_devices.py
import os
import socket
import ipaddress
import subprocess

def ping(ip):
    """Ping an IP address to check if alive (Windows)."""
    try:
        output = subprocess.check_output(
            ["ping", "-n", "1", "-w", "200", ip],
            stderr=subprocess.DEVNULL,
            universal_newlines=True
        )
        return "TTL=" in output
    except:
        return False

def scan_network():
    """Scan the 192.168.0.0/24 network."""
    network = ipaddress.ip_network("192.168.0.0/24", strict=False)
    devices = []

    for ip in network.hosts():
        ip_str = str(ip)
        if ping(ip_str):
            try:
                hostname = socket.gethostbyaddr(ip_str)[0]
            except:
                hostname = "Unknown"
            devices.append((ip_str, hostname))
            print(f"Found: {ip_str} | {hostname}")
    return devices

if __name__ == "__main__":
    print("Scanning your home network 192.168.0.0/24 ... (may take 1-2 minutes)")
    devices = scan_network()

    print("\nConnected Devices:")
    for ip, host in devices:
        print(f"IP: {ip} | Hostname: {host}")
