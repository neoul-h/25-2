# ▶ 맨 위에 학번/이름 출력
print("학번: 202104008, 이름: 김진우")

# 고정 값(문제 조건)
hourly_wage = 10030   # 시급(원)
weeks_per_month = 4   # 한 달 = 4주

# 입력받기: 일당 시간은 소수 가능 → float, 주당 일수는 정수 → int
# (input으로 문자열을 받은 뒤 숫자로 변경)
hours_per_day = float(input("일당 시간(예: 7.5): "))
days_per_week = int(input("주당 일 수(예: 5): "))

# 월급 계산: 시급 * 하루 근무시간 * 주당 근무일 * 4주
monthly_salary = hourly_wage * hours_per_day * days_per_week * weeks_per_month  # 실수값

# 정수 원단위로 반올림해서 쉼표 넣기
amount = int(monthly_salary + 0.5)  # 반올림

# 천단위로 잘라서 문자열 만들기 (//, % 같은 기본 연산만 사용)
result = ""
while amount >= 1000:
    group = amount % 1000
    amount = amount // 1000
    # 앞 그룹이 이미 있다면 3자리 맞춰 붙임
    if group < 10:
        part = "00" + str(group)
    elif group < 100:
        part = "0" + str(group)
    else:
        part = str(group)
    if result == "":
        result = part
    else:
        result = part + "," + result

# 마지막 남은 자리(천 미만)
if result == "":
    result = str(amount)
else:
    result = str(amount) + "," + result

# 출력 (문자열 이어붙이기 방식)
print("예상 월급:", result + "원")
