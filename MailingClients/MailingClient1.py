import threading
import socket
# define host address
host='127.0.0.1' #local host
port=55555
server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(host,port)
server.listen()
clients=[] # client list new client to connect with server
nicknames=[] # client identify with their nick names

def broadcast(message):
    for client in client