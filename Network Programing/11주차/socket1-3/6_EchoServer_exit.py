from socket import *  # import socket 으로 하면 오류 
from select import *

HOST = ''
PORT = 10000
BUFSIZE = 1024
ADDR = (HOST, PORT)
# 소켓 생성
serverSocket = socket(AF_INET, SOCK_STREAM)
## socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 소켓 주소 정보 할당
serverSocket.bind(ADDR)
print('바인드')
# 연결 수신 대기 상태
serverSocket.listen(10)
print('대기')
# 연결 수락
clientSocekt, addr_info = serverSocket.accept()
print('연결 수락: client 정보', addr_info)

# 클라이언트로부터 메시지를 가져옴
while True:
  data = clientSocekt.recv(BUFSIZE)
  msg = data.decode()
  print(' 받은 데이터 : ',msg)
  if msg == 'exit': # exit라는 메세지를 받으면 종료
    break
  clientSocekt.sendall(data)

# 소켓 종료
clientSocekt.close()
serverSocket.close()
print('종료')