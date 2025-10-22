#Lab5_1
#카페 메뉴 보여주기

cafeMenu = "아메리카노", "카페라떼", "바닐라라떼","코코넛스무디"
#cafeMenu = ["아메리카노", "카페라떼", "바닐라라떼","코코넛스무디"]

print("[[메뉴]]")
num = 1
for m in cafeMenu:
  print(f"{num}. {m}")
  num = num + 1