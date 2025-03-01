import socket
import threading

serverPort = 20000

UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDP.bind(('', serverPort))  #binds socket to the server IP address and it's port

TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP connection will be only used for file exchange, while the rest will use UDP
TCP.bind(('', serverPort))  #binds socket to the server IP address and it's port
TCP.listen(1)

print('[SERVER READY] Waiting for connection...')

clients = {} #tuple to store the client and his address

# will forward the message to all clients, except the one sending the message
def forwardToClients(message, clientAddress):
    for client in clients:
        if client != clientAddress:
            UDP.sendto(message.encode(), client)

# function that will receive the file sent by the client
def receiveFile(con, name):
    file = open(name,'wb')
    while True:
        data = con.recv(1024)   # buffer size set to 1024
        if not data:
            break
        file.write(data)
    file.close()
    print("File received")

    return

# function that will send the file requested by the client
def sendFile(conn, name):
    error = ''
    try:
        file = open(name,'rb')
        for msg in file.readlines():
            conn.send(msg)
        file.close()
        print('File sent')
    except FileNotFoundError:
        error = 'INFO:File does not exist'
        print('File does not exist')

    return error

#MAIN SERVER LOOP
def SERVER_LOOP():
    while True:

        message, clientAddress = UDP.recvfrom(2048) #buffer size set to 2048
        message = message.decode().split(":")

        if message[0] == 'USER':
            clients[clientAddress] = message[1]        
            print(f'New client connected as {message[1]}')
            text = f"INFO:{message[1]} connected."
            forwardToClients(text, clientAddress)

        elif message[0] == 'MSG':  
            print(f'{clients[clientAddress]} sent a message')
            text = f"MSG:{clients[clientAddress]} said: {message[1]}"
            forwardToClients(text, clientAddress)

        elif message[0] == 'LIST':
            print(f'{clients[clientAddress]} requested a list of clients that are connected at the moment')
            text = 'INFO:Connected clients:\n'
            for index, client in enumerate(clients):
                text += clients[client]
                if index != len(clients) - 1:
                    text += ", "
            UDP.sendto(text.encode(), clientAddress)

        elif message[0] == 'FILE':
            print(f'{clients[clientAddress]} sent a file')
            conn, clientTCP = TCP.accept()
            receiveFile(conn, message[1])
            text = f"INFO:{clients[clientAddress]} sent {message[1]}"
            forwardToClients(text, clientAddress)
            conn.close()
        
        elif message[0] == 'GET':
            print(f'{clients[clientAddress]} requested a file')
            conn, clientTCP = TCP.accept()
            text = sendFile(conn, message[1])
            if len(text):
                UDP.sendto(text.encode(), clientAddress)
            conn.close()

        elif message[0] == 'BYE': 
            print(f'{clients[clientAddress]} left')
            text = f"INFO:{clients[clientAddress]} left"
            forwardToClients(text, clientAddress)
            del clients[clientAddress] # remove clientAddress from list of connected clients
            UDP.sendto('INFO:disconnect'.encode(), clientAddress) # remove client from the server

        if len(clients) == 0:
            print('No more clients connected, the server will be closed')
            break

    TCP.close()
    return

#threading to allow concurrent execution of multiple tasks enabling parallelism and efficient
t1 = threading.Thread(target=SERVER_LOOP, args=())
t1.start()
       