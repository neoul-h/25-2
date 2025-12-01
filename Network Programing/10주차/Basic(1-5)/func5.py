class cat:
    def __init__(self, name, color):
        self.name = name
        self.color = color
    def meow(self):
        print('내 이름은 {} 색은 {}, 야옹야옹'.format(self.name, self.color))
    def __str__(self) :
        return 'cat(name={}, color={})'.format(self.name, self.color)
    def set_age(self, age):
        if age > 0:
            self.age=age
    def get_age(self):
        return self.age

nabi = cat('나비', '검정')
nero = cat('네로', '흰색')
mimi = cat('미미', '갈색')
print(nabi)
nero.set_age(4)
nero.meow()
print(nero.get_age())
mimi.meow()