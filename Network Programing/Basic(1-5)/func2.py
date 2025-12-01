def greet1(name):
    print('Hello', name, '씨')

greet1('홍길동')
# greet1(input('이름을 입력하세요: '))

def greet2(*names):
    for name in names:
        greet1(name)

greet2('홍길동', '양만춘', '이순신')