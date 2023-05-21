import socket
import os
import getpass
import threading

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostbyname(socket.gethostname())
server_addr = (host, 10000)

try:
    # Connect to the server
    client.connect(server_addr)
    os.system('clear')
    print("Connected to the server")
    username = input("Enter your username: ")

    if username == "admin":
        password = getpass.getpass("Enter your password: ")




    stop_thread = False

    def receive_data():
        broadcast_sent = True
        while True:
            global stop_thread
            if stop_thread:
                break

            try:
                #if the server's message is "Username" then the client will send the username
                #or else the client will print the message out
                message = client.recv(1024).decode()

                #send the client's username to the server
                if message == "Username: ":
                    client.send(username.encode())
                    next_message = client.recv(1024).decode()

                    #if the server send "Password" then the client will send the password
                    if next_message == "Password":
                        client.send(password.encode())
                        if client.recv(1024).decode() == "DENIED":
                            print("Connection denied")
                            stop_thread = True
                    
                else:
                    print(message)


            except:
                if not broadcast_sent:
                    print("Disconnected from the server")
                    broadcast_sent = False
                client.close()
                break



    def chat():
        while True:
            if stop_thread:
                client.close()
                break
            else:
                message = f'{username}: {input("")}'
                if message[len(username)+2:].startswith("/"): #skipping through the "username: " only take the input
                    if username == 'admin':
                        if message[len(username)+2:].startswith("/kick"):
                            client.send(f"KICK {message[len(username)+8:]}".encode())
                        elif message[len(username)+2:].startswith("/ban"):
                            client.send(f"BAN {message[len(username)+7:]}".encode())
                    
                    else:
                        print("Permission denied")

                elif message == f'{username}: quit':
                    client.send(f'{username} has left the chat'.encode())
                    break

                else:
                    client.send(message.encode())

        client.close()

    receive_data_thread = threading.Thread(target=receive_data)
    receive_data_thread.start()

    chat_thread = threading.Thread(target=chat)
    chat_thread.start()


except ConnectionRefusedError:
    os.system('clear')
    print("Connection error")