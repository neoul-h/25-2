import socket
import sys 
import threading

HOST = '127.0.0.1' # 서버 주소
PORT = 5000        # 서버 포트
BUFF_SIZE = 1024
ADDR = (HOST, PORT)

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   # 서버 소켓이랑 주소체계와 TCP 맞춰 줘야

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
