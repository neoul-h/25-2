# ▶ 맨 위에 학번/이름 출력
print("********************************")
print("학번: 202104008, 이름: 김진우")
print("********************************")

# -----------------------------
# 맨 위에 학번과 이름을 출력하고, 주어진 8마리 Pet 객체의 정보를 화면에 출력합니다.
# -----------------------------

# Pet 클래스 정의
#   - 속성: region(지점/지역), category(고양이 or 강아지), species(종), name(이름)
#   - 메소드: displayInfo() -> 문자열(String) 반환
class Pet:
    # 생성자: 객체가 만들어질 때 네 가지 정보를 받아서 멤버 변수에 저장
    def __init__(self, region, category, species, name):
        self.region = region      # 지점(지역)
        self.category = category  # 분류: 고양이 / 강아지
        self.species = species    # 종
        self.name = name          # 이름

    # 정보 출력용 문자열을 만들어서 "반환"하는 메소드 (SmartPhone 예제처럼 사용) :contentReference[oaicite:1]{index=1}
    def displayInfo(self):
        return f"지점: {self.region}, 분류: {self.category}, 종: {self.species}, 이름: {self.name}"


# 퀴즈에서 주어진 8마리 Pet 객체 생성 (슬라이드의 데이터 그대로 사용) :contentReference[oaicite:3]{index=3}
pet1 = Pet("서울본점", "고양이", "랙돌", "까망이")
pet2 = Pet("인천지점", "고양이", "코리안 숏 헤어", "비호")
pet3 = Pet("수원동탄", "강아지", "래브라도 리트리버", "다비")
pet4 = Pet("수원동탄", "강아지", "말티푸", "럭키")
pet5 = Pet("수원동탄", "고양이", "코리안숏헤어", "배꼽이")
pet6 = Pet("수원동탄", "고양이", "코리안숏헤어", "밀크")
pet7 = Pet("수원동탄", "강아지", "포메라니안", "봉구")
pet8 = Pet("김포지점", "고양이", "먼치킨", "아훌")

# 각 반려동물의 정보 출력
#  displayInfo()는 문자열을 반환하므로, print()로 화면에 출력
print(pet1.displayInfo())
print(pet2.displayInfo())
print(pet3.displayInfo())
print(pet4.displayInfo())
print(pet5.displayInfo())
print(pet6.displayInfo())
print(pet7.displayInfo())
print(pet8.displayInfo())
