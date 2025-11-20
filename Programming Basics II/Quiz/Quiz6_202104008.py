# ▶ 맨 위에 학번/이름 출력
print("********************************")
print("학번: 202104008, 이름: 김진우")
print("********************************")

# (1) 좌석 딕셔너리 생성 - 모든 좌석을 'O'(가능상태)로 초기화
seats = {
    "A1": "O", "A2": "O", "A3": "O",
    "A4": "O", "A5": "O"
}

# (2) 초기 좌석 상태 출력 (|상태|탭 형식)
print("\n[초기 좌석 상태]")
for key in seats:
    print(f"{key}: |{seats[key]}|\t", end="")
print("\n")

# (3) 사용자 입력: 예약할 좌석 번호 입력받기
num = input("예약할 좌석 번호를 입력하세요 : ")

# 입력받은 번호를 이용해 좌석키를 만들기 ("A" + 번호)
seat_key = "A" + num

# (4) 좌석 존재 여부 확인 후 상태 변경
if seat_key in seats:
    seats[seat_key] = "X"   # 예약불가로 변경
    print(f"{seat_key} 좌석이 예약되었습니다.")
else:
    print("잘못된 좌석 번호입니다.")

# (5) 변경된 좌석 상태 출력
print("\n[현재 좌석 상태]")
for key in seats:
    print("|", seats[key], "|\t", end="")
print("\n")