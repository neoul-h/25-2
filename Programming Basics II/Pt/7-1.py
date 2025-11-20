#Lab7_1
#파일 이름을 입력받아 이름과 확장자 구분하여 출력

ok = True

while ok:
  #사용자 입력
  filename = input("파일명 : ")

  #확장자 검사
  #조건식 순서 중요
  if filename.count('.') < 1 or len(filename[filename.rindex('.')+1:]) <= 0:
    print("확장자가 없습니다.")

  else: #다 통과하면 반복문 종료
    ok = False

idx = filename.rindex('.')
print(f"\n파일명 : {filename[:idx]}")
print(f"확장자 : {filename[idx+1:]}")