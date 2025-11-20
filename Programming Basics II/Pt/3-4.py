#Lab3_4
#좌석 및 인원 수를 입력 받아 티켓 계산하는 프로그램

#좌석 타입 입력
seatType = input("좌석 클래스(VIP, R, S, A, B) : ")
#price = 0; #여기에 선언안해도됨

#좌석 값 검사
if seatType == "VIP" or seatType == "R" or seatType == "S" or seatType == "A" or seatType == "B":
	
	#수량 입력
	count = int(input("수량 : "))
	
	#좌석에 따른 표 가격
	if seatType == "VIP" :
		price = 160000
	elif seatType == "S" :
		price = 140000
	elif seatType == "R" :
		price = 100000
	elif seatType == "A" :
		price = 80000
	elif seatType == "B" :
		price = 60000
		
	#결과값 출력
	print(f"{seatType}석 {count}개 ===> 총 {price*count}원")
	
else :
	print("!!!잘못입력하였습니다!!!")