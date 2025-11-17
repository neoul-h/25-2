# -------------------------------------------------
# [프로그램 설명]
# 이 프로그램은 상담 예약 시스템이다.
# 월~금 / 9시~13시 시간대에 대해 예약 가능 여부를 딕셔너리로 관리하고,
# 메뉴(1.예약하기 / 2.예약조회 / 3.종료하기)를 반복해서 수행한다.
#
# [데이터 구조 설명]
# days  : 요일 목록 ["월","화","수","목","금"]
# times : 시간대 목록 ["9","10","11","12","13"]
# reserve_table : 딕셔너리
#    - key  : "요일+시간" 문자열 (예: "월9", "수11")
#    - value:
#         "O"   -> 아직 예약 없음 (예약 가능)
#         "X"   -> 점심시간이라 예약 불가(12시, 13시)
#         "이름" -> 이미 예약된 상태 (예: "홍길동")
#
# [로직 설명]
# 1) 프로그램 시작 시 학번/이름을 출력한다.
# 2) 월~금 / 9~13시 전체 시간대를 돌면서 reserve_table을 채운다.
#    - 12시, 13시는 "X"
#    - 나머지 시간(9,10,11)은 "O"
# 3) 초기 상담 예약 테이블을 한 번 화면에 보여준다.
# 4) 메뉴(1,2,3)를 한 번만 출력한다.
# 5) while True 반복문 안에서
#    - "1"이면 예약하기:
#        · 이름 입력
#        · 요일/시간 입력
#        · 없는 시간대면 "잘못된 시간대입니다."
#        · 점심시간("X")이면 "!!!!!점심시간!!!!!"
#        · 이미 사람이 있으면 "예약이 있습니다."
#        · 비어 있으면 이름 기록
#    - "2"이면 예약조회:
#        · 전체 슬롯을 돌며
#          "O"      -> "월9시 ok"
#          이름문자열 -> "월10시 예약자:홍길동"
#          "X"는 출력 안 함
#    - "3"이면 종료:
#        · "[[[[[[[[종료]]]]]]]]" 출력 후 break
#    - 그 외 번호면:
#        · "*****잘못입력하였습니다*****"
#
# 이 코드는 if/elif/else, for, while True, break, continue,
# 리스트, 딕셔너리, 문자열 연결, input(), print() 등
# 수업 시간에 다룬 문법만 사용한다.
# -------------------------------------------------

print("학번: 202104008, 이름: 김진우")

# 요일과 시간대를 리스트로 정의
days = ["월", "화", "수", "목", "금"]
times = ["9", "10", "11", "12", "13"]

# 예약 정보를 담을 딕셔너리 생성
reserve_table = {}

# 상담 가능 시간표 초기화
# 12시, 13시는 점심시간으로 "X"
# 나머지(9,10,11)는 예약 가능 "O"
for d in days:
    for t in times:
        key = d + t  # 예: "월9", "수11"
        if t == "12" or t == "13":
            reserve_table[key] = "X"
        else:
            reserve_table[key] = "O"

# 초기 상담 예약 테이블 출력
print()
print("[상담 예약 테이블]")
print()
print("월 화 수 목 금")

for t in times:
    # 보기 좋게 "9시" 줄 앞에는 공백 하나
    if t == "9":
        row_text = " " + t + "시"
    else:
        row_text = t + "시"

    # 해당 시간의 월~금 상태 붙이기
    for d in days:
        key = d + t
        row_text = row_text + " " + reserve_table[key]

    print(row_text)

# 메뉴 출력 (한 번만)
print()
print("[메뉴]")
print("1.예약하기")
print("2.예약조회")
print("3.종료하기")

# 무한 반복으로 메뉴 선택 받기
while True:
    sel = input("\n선택:")

    # 1. 예약하기
    if sel == "1":
        name = input("예약자 이름:")

        # 올바른 예약이 완료될 때까지 반복
        while True:
            day_input = input("요일(월/화/수/목/금):")
            time_input = input("시간(9/10/11/12/13):")

            key_try = day_input + time_input  # 예: "수11"

            # 1) 해당 요일+시간 조합이 실제로 존재하는지 확인
            if key_try in reserve_table:
                # 2) 점심시간인지 확인
                if reserve_table[key_try] == "X":
                    print("!!!!!점심시간!!!!!")
                    continue

                # 3) 이미 예약된 상태인지 확인
                if reserve_table[key_try] != "O":
                    print("예약이 있습니다.")
                    continue

                # 4) 여기까지 왔으면 예약 가능 -> 이름 기록
                reserve_table[key_try] = name
                # 예약 성공 후 내부 while 종료
                break
            else:
                # 존재하지 않는 시간대
                print("잘못된 시간대입니다.")
                continue

        # 다시 메인 while로 돌아가서 다음 선택 받음

    # 2. 예약조회
    elif sel == "2":
        print()
        print("[예약조회]")

        # 시간 순서, 요일 순서대로 확인
        for t in times:
            for d in days:
                key_check = d + t
                value_now = reserve_table[key_check]

                # 예약 가능
                if value_now == "O":
                    print(d + t + "시 ok")
                # 점심시간 "X" 는 출력 안 함
                elif value_now != "X":
                    # value_now 가 이름인 경우
                    print(d + t + "시 예약자:" + value_now)

        # 조회 끝나면 다시 메뉴 반복

    # 3. 종료
    elif sel == "3":
        print("[[[[[[[[종료]]]]]]]]")
        break  # 전체 while 종료 -> 프로그램 끝

    # 잘못된 메뉴 번호
    else:
        print("*****잘못입력하였습니다*****")
        # 다시 while 처음으로
