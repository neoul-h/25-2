#Lab6_2
#인구 파악
guPopul = ['강남구', '233363',
'강동구', '199088',
'강북구', '144410',
'강서구', '267442',
'관악구', '273736',
'광진구', '166638',
'구로구', '180027',
'금천구', '114402',
'노원구', '217272',
'도봉구', '138120']

d = {}
for i in range(0, len(guPopul), 2):
  d[guPopul[i]] = int(guPopul[i + 1])

#인구 입력 받기
num = int(input("비교할 인구를 입력하세요 : "))

#딕셔너리에 있는 구/인구 정보와 인구 비교
count = 0
for gu, population in d.items():
  if population < num:
    print(f"{gu}:{population}")
    count += 1 #출력된 구가 있음

if count == 0: #count == 0 이면 출력된 구가 없음
    print(f"인구가 {num}보다 작은 구가 없습니다")
else:
   print("*********************")
   print(f"총 {count}개의 구 존재") #개수 출력