 # we use a socket to connect with certain target ip address on a specific port
 # if succede its mean port is open and if not that mean port is closed
 # PORT SCAN METHOD
import socket

   # define target here
   # it can be any network ip address but practice it only your network
target='127.0.0.1'

def portscan(port):
     try:
        #AF_INET (this socket is internet socket)
        #SOCK_STREAM which tell we are using tcp instead of Udp
            sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        #socket connect method
        # first part is target which is ip address and second is port
            sock.connect((target,port))
            return True
     except:
            return False
#print(portscan(20))
for port in range(1,1024):
    result=portscan(port)
    if result:
        print("Port is {} open".format(port))
    else:
        print("Port is {} Closed".format(port))
