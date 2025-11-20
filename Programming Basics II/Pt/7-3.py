#Lab7_3
#아이디 생성하기
users = ["yangdana", "kingwang", "babobabo", "hellopython"]
isStop = True

while isStop:
  userID = input("생성할 ID : ")

  if len(userID) < 6 or len(userID) > 16:
    print("글자 수를 맞추어주세요.")
  
  elif not userID.islower():
    print("소문자가 아닙니다.")

  elif userID in users:
    print("중복된 아이디")

  else:
    print("아이디 생성")
    isStop = False #전역 변수 isStop을 False로 설정하여 반복문 종료