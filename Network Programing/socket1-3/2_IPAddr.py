# 2_IPv4Address.py
# 문자열 IP 주소를 바이너리로 변환하기(16진수)
# socket.inet_aton(ip_addr)
# 16진수 IP 주소를 문자열로 변화하기
# socket.inet_ntoa(packed_ip_addr)
# 
# <실행결과>
# IPAddress: 127.0.0.1 ==> Packed: b'\x7f\x00\x00\x01', Unpacked: 127.0.0.1
# IPAddress: 192.168.0.1 ==> Packed: b'\xc0\xa8\x00\x01', Unpacked: 192.168.0.1
import socket

for ip_addr in ['127.0.0.1','192.168.0.1']:
    packed_ip_addr = 
    unpacked_ip_addr = 
    print ('IPAddress: {} ==> Packed: {}, Unpacked: {}'.format(
        ip_addr, packed_ip_addr, unpacked_ip_addr))
    