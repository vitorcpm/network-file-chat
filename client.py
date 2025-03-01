import socket
import threading

serverName = 'IP_ADDRESS' #Use your own IPv4 address here
serverPort = 20000

UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# receive the file sent by the client
def receiveFile(conn, name):
    data = conn.recv(1024)
    if (data):
        file = open(name,'wb')
        while 1:
            file.write(data)
            data = conn.recv(1024)
            if not data:
                break
        file.close()

    return

# send the file requested by the client to him
def sendFile(conn, name):
    file = open(name,'rb')
    for message in file.readlines():
        conn.send(message)
    file.close()

    return

connected = True   #bool will be used for client disconnection

# commands that can be used by the client, runs in a loop and continuously waiting for the user input
def userInput():
    while True:
        message = input().split(" ")

        # request a list of connected clients ('/list')
        if message[0] == '/list':
            text = "LIST"
            UDP.sendto(text.encode(), (serverName, serverPort))

        # send a file ('/file 1.jpg')
        elif message[0] == '/file':  
            TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
            TCP.connect((serverName, serverPort))
            text = "FILE:" + message[1]
            UDP.sendto(text.encode(), (serverName, serverPort))
            sendFile(TCP, message[1])
            TCP.close()

        # get the file ('/get 1.jpg')
        elif message[0] == '/get':            
            TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            TCP.connect((serverName, serverPort))
            text = "GET:" + message[1]
            UDP.sendto(text.encode(), (serverName, serverPort))
            receiveFile(TCP, message[1])
            TCP.close()

        # disconnect from server (/bye)
        elif message[0] == '/bye':
            text = "BYE"
            UDP.sendto(text.encode(), (serverName, serverPort))
            connected = False
            break

        # send a message in the server, no need to type any command
        else:
            text = "MSG:" + " ".join(message)
            UDP.sendto(text.encode(), (serverName, serverPort))

    UDP.close()
    return

# listen the messages from the server using UDP
def listenServer():
    while connected:
        message, client = UDP.recvfrom(2048)
        message = message.decode().split(":")
        if message[0] == 'INFO':
            if message[1] == 'disconnect': # if a client is disconnected, breaks the loop and exits
                break             
            elif len(message) < 3:
                print(message[1])
            else:
                print(message[1] + ': ' + message[2])
        elif message[0] == 'MSG':
            print(message[1] + ': ' + message[2])

    return

# Starting of the execution, seen by the client 
message = input('Username: ') # requires the username from the client
text = "USER:" + message
UDP.sendto(text.encode(), (serverName, serverPort))

# threading to allow concurrent execution of multiple tasks enabling parallelism and efficient
t1 = threading.Thread(target=userInput, args=())
t1.start()
t2 = threading.Thread(target=listenServer, args=())
t2.start()
