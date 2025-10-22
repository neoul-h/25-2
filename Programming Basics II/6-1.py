#Lab6_1
#다음 문자열 sentences에서 각 알파벳 문자들의 빈도수를 구하는 프로그램 작성
sentences = """lorem ipsum dolor sit amet, consectetuer adipiscing elit.
maecenas porttitor congue massa.
fusce posuere, magna sed pulvinar ultricies, purus lectus malesuada libero, sit
amet commodo magna eros quis urna.
nunc viverra imperdiet enim.
"""

#빈 딕셔너리 생성
d = {}

for s in sentences:
  if s in d: #각 글자들이 딕셔너리에 있는지 확인
    d[s] += 1 #1 증가
  else:
    d[s] = 1 #1로 초기화

for k, v in d.items():

  #임시로 key값을 다르게 출력
  if k == ' ':
    k = "SPACE"
  elif k == '\t':
    k = "TAB"
  elif k == '\n':
    k = "NEWLINE"

  print(f"{k}:{v}") #결과 출력