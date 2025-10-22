#Lab3_2
#대인, 소인 무료입장 구분하는 프로그램

#사용자 입력
year = int(input("만 나이 : "))

#검사
if year < 3:
	print("무료 입장")
elif year <= 12:
	print("소인")
else :
	print("대인")