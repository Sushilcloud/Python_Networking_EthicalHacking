from scapy.all import sniff, IP, DNSQR
from collections import defaultdict

# Dictionary: device_ip -> set of websites
device_connections = defaultdict(set)


def process_packet(packet):
    if packet.haslayer(IP) and packet.haslayer(DNSQR):
        src_ip = packet[IP].src
        domain = packet[DNSQR].qname.decode()
        device_connections[src_ip].add(domain)
        print(f"[DNS] {src_ip} -> {domain}")


if __name__ == "__main__":
    print("Monitoring devices and websites... Press Ctrl+C to stop.")
    sniff(filter="udp port 53", prn=process_packet, store=False)

    print("\n--- Summary of Devices and Websites ---")
    for device, sites in device_connections.items():
        print(f"\nDevice {device} connected to:")
        for site in sites:
            print(f"  - {site}")
