for i in range(2, 7, 2):
    print('{0:3d} {1:4d} {2:5d}'.format(i, i*i, i*i*i))

st = 'programming'
for ch in st:
    if ch in ['a', 'e', 'i', 'o', 'u']:
        break
    print (ch, end=' ')
print()

for ch in st:
    if ch in ['a', 'e', 'i', 'o', 'u']:
        continue
    print (ch, end=' ')
print()

score_list = [76, 87, 84, 95,96,88,94,63]
print(score_list[0], score_list[3])
print( len(score_list)) 
score_list.append(33)

if 87 in score_list:
    print(True)
else:
    print(False)

print('min=', min(score_list), ' sum=', sum(score_list))


list1 = [n*10 for n in score_list]
print(list1)
list2 = list(map(lambda x: x*10, score_list))
print(list2)