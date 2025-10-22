#Lab4_2
#비밀번호 입력

pw = "cs1234"
newPw = "" 

while newPw != pw :
  newPw = input("비밀번호 입력 : ")
  if newPw == pw: break
  print("!!재입력!!")

print("***환영합니다***")