#Lab3_3
#사용자에 온도와 습도를 정수로 입력받고, 다음 조건에 맞춰 에어컨을 켜는 프로그램

#온도입력
temp = int(input("온도 : "))

#습도입력
hum = int(input("습도 : "))

#검사하여 결과출력
if (temp >= 25) and (hum >= 70):
	print("[냉방모드 ON]")
elif (temp >= 25) and (hum < 70):
	print("[제습모드 ON]")
else:
	print("[[[OFF]]]")