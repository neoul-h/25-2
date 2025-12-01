# 12주차 파일입출력 퀴즈 풀이

print("202104008 김진우")

from datetime import date  # 수업에서 사용한 모듈만 사용

# -------------------------------------------------------
# 1단계: 오늘 날짜와 각 지역의 미세먼지 지수를 dust.txt에 추가 저장
# -------------------------------------------------------

# 오늘 날짜를 "YYYY-MM-DD" 형태의 문자열로 만들기
today = date.today()
today_str = str(today)  # 예: 2025-05-31

# 오늘 미세먼지 지수 (퀴즈 슬라이드의 값으로 수정해서 사용!)
seoul = 32     # 예시 값
busan = 22     # 예시 값
daegu = 24     # 예시 값
incheon = 31   # 예시 값

# dust.txt 파일을 '추가 모드(a)'로 열어서 오늘 데이터 4줄을 덧붙이기
f = open("./res/dust.txt", "a")  # 반드시 ./res 경로 사용
f.write(today_str + ",Seoul," + str(seoul) + "\n")    # 줄바꿈까지 저장!
f.write(today_str + ",Busan," + str(busan) + "\n")
f.write(today_str + ",Daegu," + str(daegu) + "\n")
f.write(today_str + ",Incheon," + str(incheon) + "\n")
f.close()

# -------------------------------------------------------
# 2단계: 파일을 다시 읽어와서 서울의 평균 미세먼지 지수 구하기
# -------------------------------------------------------

f = open("./res/dust.txt", "r")  # 읽기 모드로 다시 열기

total = 0   # 서울 미세먼지 합계
count = 0   # 서울 데이터 개수

# 파일을 한 줄씩 읽으면서 처리
for line in f:
    line = line.strip()      # 양쪽 공백 + 줄바꿈 문자 제거 (Hint 충족)
    if line == "":           # 빈 줄은 건너뛰기
        continue

    data = line.split(",")   # [날짜, 지역, 지수] 형태의 리스트
    city = data[1]           # 지역 이름
    value = int(data[2])     # 문자열을 정수로 변환

    if city == "Seoul":      # 서울 데이터만 선택
        total = total + value
        count = count + 1

f.close()  # 파일 닫기 (수업에서 강조!)

# 평균을 계산해서 소수점 둘째 자리까지 출력
if count > 0:
    avg = total / count
    # 소수점 둘째 자리까지 표현 (예: 74.65)
    print("Seoul의 평균 미세먼지 지수:", format(avg, ".2f"))
else:
    print("Seoul 데이터가 없습니다.")
