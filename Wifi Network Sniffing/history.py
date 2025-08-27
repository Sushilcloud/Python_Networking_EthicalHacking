# traffic_sniffer.py
#scapy is a powerful Python library for network packet manipulation and analysis.


from scapy.all import sniff, IP, TCP, UDP, DNSQR
from scapy.all import *

def process_packet(packet):
    # Capture DNS requests (website lookups)
    if packet.haslayer(DNSQR):
        print(f"[DNS] {packet[IP].src} is querying {packet[DNSQR].qname.decode()}")

    # Capture HTTP traffic (unencrypted)
    if packet.haslayer(TCP) and packet.haslayer(IP):
        if packet[TCP].dport == 80 or packet[TCP].sport == 80:  # HTTP traffic
            print(f"[HTTP] {packet[IP].src} -> {packet[IP].dst}")

if __name__ == "__main__":
    print("Sniffing network traffic... Press Ctrl+C to stop.")
    sniff(filter="ip", prn=process_packet, store=False)
