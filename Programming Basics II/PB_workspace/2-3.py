#Lab2_3
#화씨 섭씨로 변환하기
#연산자 "//"와 "/"의 차이 확인하기

print("화씨 -> 섭씨")
F_temp = float(input("화씨 : "))
C_temp = (F_temp-32)*5//9
print("%.2fF -> %.wfC" %(F_temp, C_temp))
# 결과 : 31.00F -> -1.00C

print("화씨 -> 섭씨")
F_temp = float(input("화씨 : "))
C_temp = (F_temp-32)*5/9
print("%.2fF -> %.wfC" %(F_temp, C_temp))
#결과 : 31.00F -> -0.56C

print("화씨 -> 섭씨")
F_temp = float(input("화씨 : "))
C_temp = (F_temp-32)*5//9
print("%.2fF -> %.wfC" %(F_temp, C_temp))
#결과 : 65.00F -> 18.33C