import socket
HOST = '' # HOST = '127.0.0.1' 동일
PORT = 5000 # 사용하지 않는 임의의 포트
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  s.bind((HOST, PORT))
  s.listen(1)
  print('대기')
  conn, addr = s.accept() # 소켓과 (주소, 포트) 로 반환
  with conn:
    print('연결:', addr)
    while True:
      data = conn.recv(1024)
      if not data: break
      conn.sendall(data)
      print('받은 데이터:', data.decode('utf-8'))
    conn.close()
  s.close()