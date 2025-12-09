from socket import *
import sys
from time import ctime

HOST = '127.0.0.1'
PORT = 10000
BUFSIZE = 1024
ADDR = (HOST,PORT)

clientSocket = socket(AF_INET, SOCK_STREAM) # 서버에 접속하기 위한 소켓을 생성한다.

try:
  clientSocket.connect(ADDR) # 서버에 접속을 시도한다.
except Exception as e:
  print('%s:%s' %ADDR)
  sys.exit()
print('연결 성공')

while True:
  sendData = input("입력 데이터 : ")
  clientSocket.send(sendData.encode())
  if sendData == 'exit': # exit라는 메세지를 받으면 종료
    break
  data = clientSocket.recv(BUFSIZE)
  print('받은 데이터 : ', data.decode())
clientSocket.close()
print('종료')