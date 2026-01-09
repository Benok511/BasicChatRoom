import socket
import threading
import datetime

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname()) # gets host name and ip rather than hardcoding for ease of use in different networks
ADDR = (SERVER,PORT)
FORMAT = 'utf_8'
DISCONNECT = "!!IMLEAVING!!"

# setting up server with SOCK_STREAM which uses TCP and using standard IPv4 addresses
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)

server.bind(ADDR)
clients = {}

# def handle_client(conn,addr):
#     print(f"[NEW CONNECTION] {addr} connected")
#     connected = True
#     try:
#         while connected:
#             msg_length = conn.recv(HEADER).decode(FORMAT)
#             if msg_length:
#                 msg_length = int(msg_length)
#                 msg = conn.recv(msg_length).decode(FORMAT)
#                 if msg == DISCONNECT:
#                     connected = False
#                 print(f"[{addr}] {msg}")
#                 conn.send("MSG RECEIVED".encode(FORMAT))
#     except Exception as e:
#         print(e)
#     finally:
#         conn.close()


def broadcast(message,conn):
    for client in clients.copy():
        if clients[client] != conn:
            try:
                clients[client].send(message)
            except:
                clients[client].close()
                del clients[client]

def handleClientChat(conn,addr,user):
    while True:
        try:
            message = conn.recv(2048)
            if not message:
                break
            message = message.decode(FORMAT)
            time = datetime.now().strftime("%-d/%-m/%y %H:%M")
            newmsg = f"{user} {time}: {message}".encode(FORMAT)
            broadcast(newmsg,conn)
        except:
            break
    
    print(f"[DISCONNECTED] {user}")
    if user in clients:
        del clients[user]
    conn.close()




def start():
    server.listen()
    print(f'[LISTENING] server is listening on on {SERVER}')

    try:
        while True:
            conn,addr = server.accept()
            user = conn.recv(2048).decode(FORMAT)
            if user in clients:
                conn.send("USERNAME IS TAKEN".encode(FORMAT))
                conn.close()
                continue
            conn.send("ACK".encode(FORMAT))
            clients[user] = conn
            
            thread = threading.Thread(target=handleClientChat,args=(conn,addr,user),daemon=True)
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {len(clients)}") # when testing noticed one extra thread which is main program so minus 1
    except KeyboardInterrupt as e:
        print(e)
        server.close()
    


print('[STARTING] server is starting')
start()