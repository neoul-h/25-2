import socket
from threading import Thread

HOST = ''    # '127.0.0.1'
PORT = 5000  # 사용중이 아닌 포트
BUFF_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     # IPv4, TCP Socket
s.bind((HOST, PORT))
s.listen(5)
print('대기')

# send recv 함수
def client_comm(cs):  #cs: client socket 값
    while True: # 데이터 송수신
        try:
            data = cs.recv(BUFF_SIZE) 
            # 상대방으로부터 데이터 받기
            # data: byte[BUFF_SIZE] 배열
        except Exception as e: 
            # 1. 상대방이 일반적으로 프로그램 종료 비정상종료
            print("클라이언트와 연결종료")
            if cs in clientSockets:
                clientSockets.remove(cs)
            break
        else: # 에러 없으면 실행
            if not data:  # 2. client의 close()하면 여기로
                cs.close()
                if cs in clientSockets:
                    clientSockets.remove(cs)
                break
            msg = data.decode()
            if msg == 'exit': # 3. 상대방의 종료 요청
                cs.close()
                if cs in clientSockets:
                    clientSockets.remove(cs)
                break
            print('받은 데이터:',msg)
            #broadcast
            for socket in clientSockets:
                socket.send(msg.encode())


clientSockets = set() # 연결한 클라이언트들의 소켓값
while True:
    clientSocket, addr_info = s.accept() 
    # client_Socket: 클라이언트 전용 소켓, 
    # addr_info: 클라이언트 IP, port
    print('연결:', addr_info)
    clientSockets.add(clientSocket)

    t = Thread(target=client_comm, args=(clientSocket,))
    t.daemon =True # main Thread가 종료되면 함께 종료
    t.start()

print('연결종료')
clientSocket.close()
s.close()


