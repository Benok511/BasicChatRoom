
import socket
import threading


HEADER = 64
PORT = 5050
FORMAT = 'utf_8'
DISCONNECT = "!!IMLEAVING!!"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER,PORT)

# after researching the threading module more i saw we can set events to coordinate
# the send thread and the receive thread
stop_event = threading.Event()

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

'''
CLIENT IS A WIP THIS IS WHATS CAUSING ALL   THE BUGS WITH DISCONNECTS DUE TO THREADING WILL FIX
'''


def receive(client):
    '''
    receives other clients messages from the server
    '''
    while not stop_event.is_set():
        try:
            message = client.recv(2048)
            if not message:
                print('[SERVER DISCONNECTED]')
                stop_event.set()
                break
            print(message.decode(FORMAT))
        except:
            print('[RECEIVE ERROR]')
            stop_event.set()
            break


def send2(client):
    '''
    sends message to server in encoded format
    '''
    while not stop_event.is_set():
        try:
            message = input()
            client.send(f'{message}\n'.encode(FORMAT))
        except (BrokenPipeError, OSError):
            print('[CANNOT SEND, SERVER DISCONNECTED]')
            stop_event.set()
            break
        except:
            stop_event.set()
            break

while True:
    '''
    Creating connection and prompting client to register with username before chatting
    if the response is an ACK then user can chat if not reconnect - bug here but will be fixed
    '''
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    user = input("create a username: ").strip()
    if not user:
        continue
    client.send(f"{user}\n".encode(FORMAT))
    response = client.recv(1024).decode(FORMAT)

    if response == "ACK\n":
        print("UserName accepted - Welcome to chatroom")
        break
    else:
        print("Username already in use. Try again.")
        client.close()
    


receive_thread = threading.Thread(target=receive,args=(client,))
send_thread = threading.Thread(target=send2,args=(client,))

receive_thread.start()
send_thread.start()

# Keep main thread alive to avoid creating new threads on username clash
try:
    receive_thread.join()
    send_thread.join()
except KeyboardInterrupt:
    print('\n[DISCONNECTING]')
    client.close()
    

