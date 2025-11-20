#Lab4_1
#사용자로부터 숫자 5개를 입력받고, 가장 큰 값을 찾아서 출력하는 프로그램

for n in range(5) :
  
  #정수 입력
  num = int(input("정수입력 : "))

  #max값 처음 입력받은 값으로 초기화
  if n == 0:
    maxNum = num
  
  #max값 갱신
  if maxNum < num :
    maxNum = num

print(f"입력받은 가장 큰 정수 = {maxNum}")