import socket
import sys 
import threading

HOST = '127.0.0.1' # 서버 주소
PORT = 5000        # 서버 포트
BUFF_SIZE = 1024
ADDR = (HOST, PORT)

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   # 서버 소켓이랑 주소체계와 TCP 맞춰 줘야

# register of my ID to the Server
myID = input("Enter your ID: ")


to_Msg = "ID"+SEP+myID+SEP # message format ID:클라이언트ID:
s.send(to_Msg.encode())
print('사용법: 브로드캐스트하려면 BR:전달할 메시지 입력')
print(' : 특정 사용자에 전달 하려면 TO:전달할 사용자ID:전달할 메시지 입력')
print(' : 서버와 연결을 종료하려면 Q 입력')

while True:
    # input message we want to send to the server
    msg = input()
    tokens = msg.split(SEP)
    code = tokens[0] 
    # a way to exit the program

    if code.upper() == 'Q':
        to_Msg = "Quit"+SEP+myID+SEP
        s.send(to_Msg.encode())
        event.set() #listen thread 종료 시키기 위해서
        # close the socket
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        print(' 서버연결종료')
        break
    elif code.upper() == "BR" :
        to_Msg = code + SEP + myID + SEP + tokens[1] + SEP
        s.send(to_Msg.encode())
    elif code.upper() == "TO":
        to_Msg = code + SEP + myID + SEP + tokens[1] + SEP + tokens[2] + SEP
        s.send(to_Msg.encode())
    elif code.upper() == "E":
        sys.exit()
    to_Msg = ‘’
        # to_Msg 내용 초기화 Initialization

try:
    serverSocket.connect(ADDR)
    # 서버 실행중비 되어야 에러 안남
    print('연결완료')
except Exception as e:
    print('%s:%s' %ADDR)
    sys.exit()

# only recieve
def listen_from_Server():
    while True:
        msg = serverSocket.recv(BUFF_SIZE).decode()
        print("\nMsg from server:", msg)

t = threading.Thread(target=listen_from_Server)
t.daemon=True
t.start()

# send
while True:
    sendData = input("입력 데이터:")

    serverSocket.sendall(sendData.encode('utf-8'))
    # serverSocket.sendall(bytes('안녕하세요, 에코서버','utf-8'))
    # 문자열을 인코딩하여 바이트배열로 만들어 전송
    print('전송완료')  
    if sendData == 'exit': break
       # 입력 끝은 exit  로 

    #data = serverSocket.recv(BUFF_SIZE) 
    #print('받은 데이터:', data.decode('utf-8'))

serverSocket.close()
