import socket
import threading
from admin_credential import hashed_password
import hashlib


# create a socket object and bind it to the address
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostbyname(socket.gethostname())
server_addr = (host, 10000)
server.bind(server_addr)

# listening for connection
server.listen()
print("Waiting for connection...")

clients = []
usernames = []

stop_thread = False

def hash_password(password: str):
    hash_object = hashlib.sha256(password.encode())
    hex_dig = hash_object.hexdigest()
    return hex_dig



def broadcast(message):
    for client in clients:
        try:
            client.send(message.encode())
        except OSError as e:
            if e.errno == 9:
                client_index = clients.index(client)
                client.close()
                clients.remove(client)
                usernames.pop(client_index)


def handle(client):
    
    if client in clients:
        client_index = clients.index(client)
        username = usernames[client_index]

    while True:
        try:
            message = client.recv(1024).decode()
            if message.startswith("KICK"):
                name_to_kick = message[5:]
                if name_to_kick in usernames:
                    broadcast(f"{name_to_kick} was kicked by the admin")
                    kick_user(name_to_kick)
                else:
                    client.send(f"{name_to_kick} is not in the chat".encode())

            elif message.startswith("BAN"):
                name_to_ban = message[4:]
                kick_user(name_to_ban)
                print("f{name_to_ban} was banned!")
            else:
                if message.startswith("admin:"):
                    broadcast("\033[91m" + username + ": " + "\033[0m" + message[7:])
                else:
                    broadcast(message)

        except (ConnectionResetError, BrokenPipeError) as e:
            client.close()
            clients.remove(client)
            usernames.remove(username)
            break

        except OSError as e:
            if e.errno == 9:
                if client in clients:
                    client_index = clients.index(client)
                    client.close()
                    clients.remove(client)
                    usernames.pop(client_index)

    #closing the connection

    if client in clients:
        client.close()
        clients.remove(client)
        print(f'{username} has left the chat')
        usernames.remove(username)


def kick_user(name_to_kick):
    if name_to_kick in usernames:
        name_index = usernames.index(name_to_kick)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send("You have been kicked from the server".encode())
        client_to_kick.close()
        usernames.remove(name_to_kick)
        
    else:
        print("")

 

    
            
def receive():
    while True:
  
        client, client_addr = server.accept()
        print(f"Connected with {str(client_addr)}")

        for client in clients:
            # asking for client's username
            client.send("Username: ".encode())
            username = client.recv(1024).decode()

            #if client's username is admin then asks for password
            if username == "admin":
                client.send("Password".encode())
                password = client.recv(1024).decode()
                #hashes the password 
                hashed_enter_password = hash_password(password)

                if hashed_enter_password != hashed_password:
                    client.send("DENIED".encode())
                    client.close()
                    continue



            # add the client and its username to the list
            usernames.append(username)
            clients.append(client)

        # broadcast to everyone about the client's arrival
            print(f"Client's username is {username}")
            broadcast(f'{username} has joined the chat')


            client.send(f"Welcome back, {username}".encode())

        # create a thread to handle client
        thread = threading.Thread(target=handle, args=[client])
        thread.start()

receive()

