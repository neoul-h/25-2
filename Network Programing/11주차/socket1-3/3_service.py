# 3_service_name.py
# 주어진 포트번호와 프로토콜 이름으로 서비스 이름 찾기
# 실행결과
# Port: 80 ==> service name: http
# Port: 21 ==> service name: ftp
# Port: 25 ==> service name: smtp
# Port: 53 ==> service name: domain

import socket

protocol_name = 'tcp'
for port in [80, 21, 25] :
    print("Port: {} ==> service name: {}".format(
        port, )

print("Port: {} ==> service name: {}".format(
    53, ))