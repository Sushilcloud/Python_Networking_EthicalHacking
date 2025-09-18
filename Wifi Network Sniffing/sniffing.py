#!/usr/bin/env python3
"""
sniffing_with_mac.py

Passive domain monitor per device that prints MAC + IP -> domain.
Auto-detects interface if not provided. Optional vendor lookup via `manuf`.

Requirements:
  - Run as root/Administrator
  - pip install scapy psutil
  - (optional) pip install manuf  -> prints vendor names

Usage:
  sudo python3 sniffing_with_mac.py
  OR
  sudo python3 sniffing_with_mac.py --iface "Ethernet 2"
  To debug more traffic: add --bpf "port 53 or port 80 or port 443 or ip"
"""
import argparse
import json
import os
import signal
import sys
import time
from collections import defaultdict
from datetime import datetime

import psutil
from scapy.all import sniff, Raw, IP, TCP, UDP, Ether
from scapy.layers.dns import DNS

# optional vendor lookup
try:
    from manuf import manuf

    _manuf = manuf.MacParser()
except Exception:
    _manuf = None

STATE_FILE = "domains_state.json"
LOG_CSV = "domains_log.csv"
SAVE_INTERVAL = 60  # seconds

domains_by_ip = defaultdict(dict)  # ip -> {domain: last_seen}
mac_by_ip = {}  # ip -> mac (last seen)
vendor_by_mac = {}  # mac -> vendor


def detect_active_iface():
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    for iface, info in addrs.items():
        if iface in stats and stats[iface].isup:
            for addr in info:
                # AF_INET == 2 on many platforms
                if getattr(addr, "family", None) in (2,):
                    if getattr(addr, "address", "") != "127.0.0.1":
                        return iface
    return None


def save_state():
    obj = {
        "last_saved": datetime.now().isoformat(),
        "data": {ip: dict(domains) for ip, domains in domains_by_ip.items()},
        "macs": mac_by_ip,
        "vendors": vendor_by_mac,
    }
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2)
    except Exception:
        pass


def append_log(timestamp, src_mac, src_ip, domain, proto):
    line = f'{timestamp},{src_mac},{src_ip},"{domain}",{proto}\n'
    try:
        with open(LOG_CSV, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass


def create_log_header_if_missing():
    if not os.path.exists(LOG_CSV):
        try:
            with open(LOG_CSV, "w", encoding="utf-8") as f:
                f.write("timestamp,src_mac,src_ip,domain,proto\n")
        except Exception:
            pass


# --- extraction helpers (same simple parsers as before) ---
def extract_dns(pkt):
    try:
        dns = pkt[DNS]
        if dns.qr == 0 and dns.qd is not None:
            qname = (
                dns.qd.qname.decode()
                if isinstance(dns.qd.qname, bytes)
                else dns.qd.qname
            )
            return qname.rstrip(".")
    except Exception:
        pass
    return None


def extract_http_host(payload_bytes):
    try:
        s = payload_bytes.decode("utf-8", errors="ignore")
        if not s.startswith(("GET ", "POST ", "HEAD ", "PUT ", "OPTIONS ")):
            return None
        for line in s.split("\r\n"):
            if line.lower().startswith("host:"):
                host = line.split(":", 1)[1].strip()
                return host.split(":")[0]
    except Exception:
        pass
    return None


def extract_sni(payload_bytes):
    try:
        b = payload_bytes
        if len(b) < 5:
            return None
        # try find TLS record (0x16)
        if b[0] != 22:
            i = b.find(b"\x16")
            if i == -1:
                return None
            b = b[i:]
        offset = 5 + 4 + 2 + 32
        if offset >= len(b):
            return None
        # session id
        session_id_len = b[offset]
        offset += 1 + session_id_len
        if offset + 2 > len(b):
            return None
        cs_len = int.from_bytes(b[offset : offset + 2], "big")
        offset += 2 + cs_len
        if offset + 1 > len(b):
            return None
        cm_len = b[offset]
        offset += 1 + cm_len
        if offset + 2 > len(b):
            return None
        exts_len = int.from_bytes(b[offset : offset + 2], "big")
        offset += 2
        end_exts = offset + exts_len
        while offset + 4 <= end_exts:
            ext_type = int.from_bytes(b[offset : offset + 2], "big")
            ext_len = int.from_bytes(b[offset + 2 : offset + 4], "big")
            offset += 4
            if ext_type == 0x00:
                sn_offset = offset
                if sn_offset + 2 > end_exts:
                    return None
                list_len = int.from_bytes(b[sn_offset : sn_offset + 2], "big")
                sn_offset += 2
                if sn_offset + 3 > end_exts:
                    return None
                name_type = b[sn_offset]
                name_len = int.from_bytes(b[sn_offset + 1 : sn_offset + 3], "big")
                sn_offset += 3
                if sn_offset + name_len > end_exts:
                    return None
                server_name = b[sn_offset : sn_offset + name_len].decode(
                    errors="ignore"
                )
                return server_name
            offset += ext_len
    except Exception:
        pass
    return None


# ---------- packet handler ----------
def handle_pkt(pkt):
    ts = datetime.now().isoformat()
    if not pkt.haslayer(IP):
        return

    src_ip = pkt[IP].src
    src_mac = None
    if pkt.haslayer(Ether):
        src_mac = pkt[Ether].src.lower()
        mac_by_ip[src_ip] = src_mac
        if _manuf and src_mac not in vendor_by_mac:
            try:
                vendor = _manuf.get_manuf(src_mac)
                vendor_by_mac[src_mac] = vendor or ""
            except Exception:
                vendor_by_mac[src_mac] = ""

    # DNS
    if pkt.haslayer(DNS) and pkt.haslayer(UDP):
        q = extract_dns(pkt)
        if q:
            domains_by_ip[src_ip][q] = ts
            vendor = vendor_by_mac.get(src_mac, "")
            print(
                f"[DNS] {src_mac or '??'} | {src_ip} -> {q} {f'[{vendor}]' if vendor else ''}"
            )
            append_log(ts, src_mac or "", src_ip, q, "DNS")
            return

    # HTTP
    if pkt.haslayer(TCP) and pkt[TCP].dport == 80 and pkt.haslayer(Raw):
        host = extract_http_host(bytes(pkt[Raw].load))
        if host:
            domains_by_ip[src_ip][host] = ts
            vendor = vendor_by_mac.get(src_mac, "")
            print(
                f"[HTTP] {src_mac or '??'} | {src_ip} -> {host} {f'[{vendor}]' if vendor else ''}"
            )
            append_log(ts, src_mac or "", src_ip, host, "HTTP")
            return

    # TLS SNI
    if pkt.haslayer(TCP) and pkt[TCP].dport == 443 and pkt.haslayer(Raw):
        sni = extract_sni(bytes(pkt[Raw].load))
        if sni:
            domains_by_ip[src_ip][sni] = ts
            vendor = vendor_by_mac.get(src_mac, "")
            print(
                f"[TLS SNI] {src_mac or '??'} | {src_ip} -> {sni} {f'[{vendor}]' if vendor else ''}"
            )
            append_log(ts, src_mac or "", src_ip, sni, "SNI")
            return


# ---------------- main ----------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iface", help="Network interface to sniff (optional)")
    parser.add_argument(
        "--bpf",
        default="tcp port 443 or tcp port 80 or udp port 53",
        help="BPF filter (default captures DNS, HTTP, TLS)",
    )
    args = parser.parse_args()

    iface = args.iface or detect_active_iface()
    if not iface:
        print(
            "❌ Could not auto-detect an active interface. Please specify with --iface."
        )
        sys.exit(1)

    print(f"[info] Using interface: {iface}")
    print(f"[info] BPF filter: {args.bpf}")
    if _manuf:
        print("[info] manuf vendor lookup available (vendor names will be shown).")

    create_log_header_if_missing()

    def stop(sig, frame):
        print("\n[info] Saving state and exiting...")
        save_state()
        sys.exit(0)

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    sniff(iface=iface, filter=args.bpf, prn=handle_pkt, store=False)


if __name__ == "__main__":
    main()
