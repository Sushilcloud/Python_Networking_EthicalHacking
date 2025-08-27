# What this script does
# Sniff live network traffic and extra useful information such as:
# DNS requests
# HTTP Traffic

from scapy.all import sniff,IP,TCP,UDP,DNSQR
from scapy.all import *
#sniff funtion to capture network packets
# IP,TCP,UDP,DNSQR protocol layer(so scapy can recognize and decode them)

def process_packet(packet):
    #capture DNS Requests (website lookup)
    if packet.haslayer(DNSQR):
        print(f"[DNS]{packet[IP].src} is querying{packet[DNSQR].qname.decode()}")

    # capture HTTP Traffic (unencryptd)
    if packet.haslayer(TCP) and packet.haslayer(IP):
        if packet[TCP].dport==80 or packet[TCP].sport==80:  # HTTP Traffic
            print(f"[HTTP]{packet[IP].src}->{packet[IP].dst}")

if __name__=="__main__":
    print("Sniffing network traffic....press Ctrl+c to stop")
    sniff(filter="ip",prn=process_packet,store=False)