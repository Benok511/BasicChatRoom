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

clientsLock = threading.Lock()

def broadcast(message,conn):
    '''
    broadcasts a message received from a client to all other connecting clients
    threadLock on the client dict to avoid concurrency issues with threads
    '''
    # was researching threading and realised that multiple threads may access it at the same time so added a lock to prevent
    with clientsLock:
        for user, client_conn in list(clients.items()):
            if client_conn != conn:
                try:
                    client_conn.send(message)
                except:
                    client_conn.close()
                    del clients[user]


def handleClientChat(conn,addr,user):
    '''
    handles a chat from a client then broadcasts to each user
    '''
    while True:
        try:
            print(f"[DEBUG] Waiting for message from {user}...")
            message = conn.recv(2048)
            print(f"[DEBUG] Received from {user}: {message}")
            if not message:
                break
            message = message.decode(FORMAT)
            time = datetime.datetime.now().strftime("%d/%m/%y %H:%M")
            newmsg = f"{user} {time}: {message}\n".encode(FORMAT)
            broadcast(newmsg,conn)
        except:
            break
    
    print(f"[DISCONNECTED] {user}")
    if user in clients:
        del clients[user]
    conn.close()




def start():
    '''
    initial server setup allowing server to listen on port 5050
    accepts user connection prompts for username and either refuses connection
    if taken or adds to user dict and starts up the thread to handle chats
    '''
    server.listen()
    print(f'[LISTENING] server is listening on on {SERVER}:{PORT}')

    try:
        while True:
            conn,addr = server.accept()
            user = conn.recv(1024).decode(FORMAT).strip()
            if user in clients:
                conn.send("USERNAME IS TAKEN\n".encode(FORMAT))
                conn.close()
                continue
            conn.send("ACK\n".encode(FORMAT))
            clients[user] = conn
            
            thread = threading.Thread(target=handleClientChat,args=(conn,addr,user),daemon=True)
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {len(clients)}")
    except KeyboardInterrupt as e:
        print(e)
        server.close()
    


print('[STARTING] server is starting')
start() 