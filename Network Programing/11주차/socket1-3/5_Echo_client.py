import socket
HOST = '127.0.0.1'
PORT = 5000 # 서버와 같은 포트 사용
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  s.connect((HOST, PORT))
  print('연결 완료')
  s.sendall(bytes('안녕하세요 에코서버','utf-8'))
  print('전송 완료')
  data = s.recv(1024)
  print('받은 데이터:', data.decode('utf-8'))
  s.close()