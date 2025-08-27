import socket
from IPy import IP

#ipaddress=input('[+] Enter target to Scan:-')

def scan_port(ipaddress,port):
    try:
        sock=socket.socket()
        # for scan faster but accuracy will high without timout function
        sock.settimeout(0.5)
        sock.connect((ipaddress,port))
        print('[+] Port  '+ str(port)+ 'is open')
    except:
        print('[+] Port  '+ str(port)+ 'is closed')

ipaddress=input('[+] Enter target to Scan:-')
for port in range(78,82):
    scan_port(ipaddress, port)