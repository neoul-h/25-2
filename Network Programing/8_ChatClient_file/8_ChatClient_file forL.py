# client ID BR TO Q
import socket
from threading import Thread
from datetime import datetime
from pathlib import Path
from os.path import exists
import sys

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 10000 # server's port
BUF_SIZE = 1024
SEP = ":" # we will use this to separate the client name & message

# initialize TCP socket
s = socket.socket()
print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
# connect to the server
s.connect((SERVER_HOST, SERVER_PORT))
print("[+] Connected.")

def listen_for_messages():
    while True:
        try:
            message = s.recv(BUF_SIZE).decode()
            
            tokens= message.split(SEP)
            code = tokens[0]
            if code.upper() == "FILE":
                received = 0
                fromID = tokens[1]
                toID = tokens[2]
                f_name = 'img/'+tokens[3]
                f_size = int(tokens[4])

                with open(f_name, 'wb') as f:         
                    try:            
                        while received < f_size: #데이터가 있을 때까지
                            data = s.recv(BUF_SIZE)                
                            f.write(data) #1024바이트 쓴다                
                            received += len(data)
                            print("FILE recieved", received)
    
                        print('파일 %s 수신:  %d bytes' %(f_name, received))
                    except Exception as ex:
                        print(ex)
            else:
                print("\n" + message)
        except Exception as e:
            print(f"Error:{e}")

# make a thread that listens for messages to this client
t = Thread(target=listen_for_messages)
# make the thread daemon so it ends whenever the main thread ends
t.daemon = True
# start the thread
t.start()

# register of my ID to the Server
myID = input("Enter your ID: ")
to_Msg = "ID"+SEP+myID+SEP
s.send(to_Msg.encode())

while True:
    # input message we want to send to the server
    msg =  input()
    tokens = msg.split(SEP)
    code = tokens[0]
    # a way to exit the program
    if code.upper() == 'Q':
        to_Msg = "Quit"+SEP+myID+SEP
        s.send(to_Msg.encode())
        break
    
    elif code.upper() == "FILE":
        toID = tokens[1]
        filename = tokens[2]
        if not exists(filename):
            print("no file")
        else:    
            
            file_size = Path(filename).stat().st_size 
            to_Msg = code + SEP + myID + SEP + toID +SEP+ filename + SEP + str(file_size) + SEP
            print(to_Msg)
            
            s.send(to_Msg.encode())
            sent = 0
            with open(filename, 'rb') as f:
                try:
                    data = f.read(1024) #1024바이트 읽는다
                    while data: #데이터가 없을 때까지
                        sent += s.send(data) #1024바이트 보내고 크기 저장
                        data = f.read(1024) #1024바이트 읽음
                    print("Complete File tx ")
                except Exception as ex:
                    print(ex)
    to_Msg = ''  # Initialization

# close the socket
s.close()