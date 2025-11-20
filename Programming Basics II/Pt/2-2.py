#Lab2_2
#커피 원두 원산지, 무게, 무게 당 가격을 입력 받아 총 가격을 계산하여 출력.

print("[COFFEE]")
co_name = input("원산지 : ") #원산지 사용자 입력
co_weight = input("무게(g) : ") #무게 입력(문자열)
co_weight = int(co_weight) #(문자열) -> (정수형 변환)
#무게 입력 받고 문자열 -> 정수형으로 변환
co_price = int(input("무게 당 가격(원) : "))

#결과 출력
print("[%s] %dg -> %d원" %(co_name, co_weight, co_price*co_weight))