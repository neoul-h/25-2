def print_sum():
    a=100
    b=200
    result = a+b
    print('내부:a=',a, '과 ', b, '의 합은', result, '입니다')

a=10
b=10
print_sum()
result = a+b
print('외부:a=',a, '과 ', b, '의 합은', result, '입니다')