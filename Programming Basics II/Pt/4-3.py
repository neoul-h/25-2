#Lab4_3
#피라미드 출력

output = ""

for i in range(1, 15):
  for j in range(14, i, -1):
    output += ' '
  for k in range(0, 2 * i - 1):
    output += '*'
  output += '\n'

print(output)