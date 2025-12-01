from PIL import Image, ImageDraw, ImageFont

width, height = 1179, 2556
bg = (255, 245, 230)

img = Image.new("RGB", (width, height), bg)
draw = ImageDraw.Draw(img)

cx = width // 2

# Fonts
font_title = ImageFont.load_default()
font_sub = ImageFont.load_default()
font_btn = ImageFont.load_default()
font_small = ImageFont.load_default()

# Logo
draw.text((cx - 80, 200), "Localy", fill="black", font=font_title)
draw.text((cx - 180, 270), "지금 여기, 나만을 위한 로컬 추천", fill=(100, 100, 100), font=font_sub)

# Cloud + GPS icon
draw.ellipse((cx - 200, 450, cx + 200, 800), outline="gray", width=4)
draw.ellipse((cx - 70, 560, cx + 70, 700), outline="gray", width=4)

draw.text((cx - 150, 900), "어디 갈지 고민되나요?", fill="black", font=font_sub)
draw.text((cx - 180, 950), "기분과 위치만 알려주세요!", fill="black", font=font_sub)

# Main Button
button_color = (255, 135, 140)
draw.rounded_rectangle((200, 1300, width - 200, 1450), radius=80, fill=button_color)
draw.text((cx - 160, 1370), "지금 근처 추천 받기", fill="white", font=font_btn)

# Links
draw.text((cx - 120, 1550), "로그인 / 회원가입", fill="black", font=font_sub)
draw.text((cx - 120, 1610), "서비스 둘러보기", fill="black", font=font_sub)

draw.text((cx - 200, 2400), "위치 정보는 추천 기능에만 사용돼요.", fill=(120, 120, 120), font=font_small)

img.save("Localy_initial_screen.jpg")
img.save("Localy_initial_screen.pdf")
print("DONE! 파일이 생성되었습니다 🎉")
