# ▶ 맨 위에 학번/이름 출력
print("********************************")
print("학번: 202104008, 이름: 김진우")
print("********************************")

score = 0  # 맞춘(=Yes) 개수로 점수 계산

# 1번 질문
ans1 = input("Q1. 물건을 자주 잃어버리는 편이다. (Y/N): ")
if ans1 == 'Y' or ans1 == 'y':   # 문자열 비교 + 논리연산자(or) 사용
    score = score + 1            # 점수 1점 추가

# 2번 질문
ans2 = input("Q2. 대화를 하다가 딴 생각을 자주한다. (Y/N): ")
if ans2 == 'Y' or ans2 == 'y':
    score = score + 1

# 3번 질문
ans3 = input("Q3. 자리에 자주 앉아있기 힘들다. (Y/N): ")
if ans3 == 'Y' or ans3 == 'y':
    score = score + 1

# 4번 질문
ans4 = input("Q4. 계획없이 즉흥적으로 행동할 때가 많다. (Y/N): ")
if ans4 == 'Y' or ans4 == 'y':
    score = score + 1

# 5번 질문
ans5 = input("Q5. 실수나 빠뜨리는 일이 많다. (Y/N): ")
if ans5 == 'Y' or ans5 == 'y':
    score = score + 1

# 점수 현황
print(f"점수: {score}")  # 최종 판정 전에 현재 점수를 보여줌

# 최종 판정: if-else 사용 (조건: 3점 이상이면 '성향 있다')
if score >= 3:
    print("ADHD 성향이 있습니다.")
else:
    print("ADHD 성향이 뚜렷하지 않습니다.")