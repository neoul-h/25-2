def get_ans(ans):
    if ans in ['예', "아니오"]:
        print('정상')
    else:
        raise ValueError('입력확인')  ## 개발자가 예외 발생
    
while True:
    try:
        ans = input('예/아니오 로 입력하시오: ')
        get_ans(ans)
        break
    except Exception as e:
        print('error', e)

try:
    a,b = input('두 수를 입력하시오: ')  # 89 일의자리 두수
    result = int(a) / int(b)
except ZeroDivisionError:
    print("Zero Division Errer")
except ValueError:
    print('ValueError')
except Exception as e:  
    print('error:', e)
else:
    print('{}/{}={}'.format(a,b,result))
finally:
    print('수행완료')