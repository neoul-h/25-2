#Lab7_2
#영화 리뷰 텍스트 중 일부를 전처리 과정
line = "One of the other reviewers has mentioned that after watching just 1 Oz episode you'll be hooked. They are right, as this is exactly what happened with me.<br /><br />The first thing that struck me about Oz was its brutality and unflinching scenes of violence, which set in right from the word GO. Trust me, this is not a show for the faint hearted or timid. This show pulls no punches with regards to drugs, sex or violence. Its is hardcore, in the classic use of the word.<br /><br />It is called OZ as that is the nickname given to the Oswald Maximum Security State Penitentary. It focuses mainly on Emerald City, an experimental section of the prison where all the cells have glass fronts and face inwards, so privacy is not high on the agenda. Em City is home to many..Aryans, Muslims, gangstas, Latinos, Christians, Italians, Irish and more....so scuffles, death stares, dodgy dealings and shady agreements are never far away.<br /><br />I would say the main appeal of the show is due to the fact that it goes where other shows wouldn't dare. Forget pretty pictures painted for mainstream audiences, forget charm, forget romance...OZ doesn't mess around. The first episode I ever saw struck me as so nasty it was surreal, I couldn't say I was ready for it, but as I watched more, I developed a taste for Oz, and got accustomed to the high levels of graphic violence. Not just violence, but injustice (crooked guards who'll be sold out for a nickel, inmates who'll kill on order and get away with it, well mannered, middle class inmates being turned into prison bitches due to their lack of street skills or prison experience) Watching Oz, you may become comfortable with what is uncomfortable viewing....thats if you can get in touch with your darker side."
print(f"전처리 전 글자수 : {len(line)}")

#1) 대문자 -> 소문자 변환
line = line.lower()

#2) 태그, 특수문자 및 숫자 제거
clean_text = ""
inside_tag = False
for char in line: #한 글자씩 검사

  if char == '<':
    inside_tag = True

  elif char == '>':
    inside_tag = False

  elif not inside_tag and (char.isalpha() or char.isspace()) :
    clean_text += char

#3)불용어 제거
stopWords = ['a', 'an', 'the']
line = clean_text
clean_text = ""
for word in line.split(): #띄어쓰기로 분리 후 한 단어씩
  if not word in stopWords : #검사
    clean_text += word+" "

#결과
print(f"전처리 후 글자수 : {len(clean_text)}")
print(clean_text)