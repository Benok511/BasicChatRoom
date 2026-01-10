
import socket
import threading


HEADER = 64
PORT = 5050
FORMAT = 'utf_8'
DISCONNECT = "!!IMLEAVING!!"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER,PORT)

#old code from previous try but keeping it in case i feel like revisiting
# def send(msg):
#     message = msg.encode(FORMAT)
#     msgLen = len(message)
#     encodedLen = str(msgLen).encode(FORMAT)
#     encodedLen += b' ' * (HEADER - len(encodedLen))
#     client.send(encodedLen)
#     client.send(message)
#     response = client.recv(2048).decode(FORMAT)
#     print(response)

def receive():
    '''
    recieves other clients messages from the server  
    '''
    while True:
        try:
            message = client.recv(2048)
            if not message:
                print('[SERVER DISCONNECTED]')
                break
            try:
                print(message.decode(FORMAT))
            except UnicodeDecodeError:
                continue
        except:
            break


def send2():
    '''
    sends message to server in encoded format
    '''
    while True:
        message = input()
        client.send(message.encode(FORMAT))

while True:
    '''
    Creating connection and prompting client to register with username before chatting
    if the response is an ACK then user can chat if not reconnect - bug here but will be fixed
    '''
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    user = input("create a username: ")
    client.send(user.encode(FORMAT))
    response = client.recv(1024).decode(FORMAT)

    if response == "ACK":
        print("UserName accepted - Welcome to chatroom")
        break
    else:
        print("Username already in use. Try again.")
        client.close()
    
    

receive_thread = threading.Thread(target=receive, daemon=True)
send_thread = threading.Thread(target=send2, daemon=True)

receive_thread.start()
send_thread.start()

# Keep main thread alive to avoid creating new threads on username clash
try:
    receive_thread.join()
    send_thread.join()
except KeyboardInterrupt:
    print('\n[DISCONNECTING]')
    client.close()

