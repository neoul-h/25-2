# 1_get_hostname.py
#
# socket.gethostname() 함수는 로컬 컴퓨터의 이름 반환
# socket.gethostbyname(host_name) 함수는 호스트 이름의 IP 주소 반환
# 외부 호스트의 IP 주소 얻기
# remote_ip_address= gethostbyname(외부 호스트의 도메인 이름의 문자열)
# 
# <실행결과>
# host name: DESKTOP-TQ836S2
# IP address: 220.67.154.156
# IP address of www.python.org:146.75.48.223
import 
from 
import 

host_name = 

ip_address =
 
print (f"host name: {host_name}")
print (f"IP address: {ip_address}")
    
# 외부 호스트의 IP 주소 얻기
# remote_ip_address= gethostbyname(외부 호스트의 도메인 이름의 문자열)
remote_host = 'www.python.org'
try:
    remote_ip_address = 
    print(f"IP address of {remote_host}:{remote_ip_address}")
except IOError as e:
   print('Reading error: {}'.format(str(e)))
# try: A 무조건 실행
#       A
# except: A에서 에러나면 에러 처리
# else: A에서 에러 안나면 실행
# finally: 마지막에 무조건 실행
