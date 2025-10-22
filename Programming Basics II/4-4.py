#Lab4_4
#은행업무

balace = 400000
menu = -1

while menu != 0:

  #메뉴 보여주기
  print("\n 1. 입금")
  print("2. 출금")
  print("[종료는 0 입력]")

  #메뉴번호 입력 받기
  menu = int(input("번호 : "))

  if menu == 1:
    income = int(input("입금 금액 : "))
    balance = balance + income
    print(f"잔액 : {balance}원")

  elif menu == 2:
    amount = int(input("출급 금액 : "))

    while balance-amount < 0:
      amount = int(input("출금 금액 : "))

  balance = balance - amount
  print(f"잔액 : {balance}원")