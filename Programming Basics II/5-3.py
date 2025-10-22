#Lab5_3

cafeMenu = ["아메리카노", 2700], ["카페라떼 ",3500], ["바닐라라떼", 4200], ["코코넛스무디",5800]

print("[[메뉴]]")
num = 1
for m in cafeMenu:
  print(f"{num}. {m[0]}\t{m[1]}원")
  num = num + 1

#장바구니 추가
cart=[] #리스트로 초기화
num = 1
while num != 0:
  num = int(input("번호(종료는 0) : "))

  #예외처리
  if num<0 or num >= len(cafeMenu):
    print("!!!잘못입력!!!")

  #종료 문구 출력
  elif num == 0:
    print("[[[종료]]]")

  #실제 메뉴추가
  else:
    cart.append(cafeMenu[num-1])

#결과 출력
total = 0
print("\n\n********주문내역********")
for c in cart:
  print(f"{c[0]}\t{c[1]}원") #메뉴출력
  total = total + c[1] #총 금액계산

print("********************")
print(f"총 개수 \t{len(cart)}개")
print(f"총 금액 \t{total}원")
print("********************")