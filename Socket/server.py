import _socket
import socket
import threading

PORT=5050
SERVER='192.168.56.1'
# below code automaticaly hostname
SERVER=socket.gethostbyname(socket.gethostname())
ADDR=(SERVER,PORT)
print(SERVER)
# NOW CREATE A SOCKET (
server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# bind this two address
server.bind(ADDR)

def handle_client(conn,addr):
    pass
def start():
    server.listen()
    while True:
        conn,addr=server.accept()
        thread=threading.Thread(target=handle_client())
print("[SARTING] server is starting...")
start()