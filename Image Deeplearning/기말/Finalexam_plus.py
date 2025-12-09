############################################################
# 9주차 - 영상 처리 II (감마 보정 / 블러 & 엠보싱 / 보간법 비교)
# 이 파일 전체는 "이미지 딥러닝" 수업에서 배운
# 기본 영상 처리 + 딥러닝 모델들을 한 번에 모아 둔 연습 코드입니다.
############################################################
import cv2 as cv          # OpenCV: 이미지/영상 처리 라이브러리
import numpy as np        # NumPy: 수치 계산(배열, 행렬) 라이브러리

# ---------------------------------------------------------
# [1] 감마 보정 (Gamma Correction)
#   - 언제 쓰나?
#       * 사진이 너무 어두울 때 → 전체를 밝게 만들고 싶을 때
#       * 밝은 부분/어두운 부분의 대비(컨트라스트)를 조절하고 싶을 때
#   - 핵심 아이디어:
#       * 픽셀 값(0~255)을 0~1 사이로 바꾼 뒤, f(x) = x^gamma 를 적용
#       * gamma < 1 : 어두운 부분을 더 밝게 만들어서 전체적으로 밝아짐
#       * gamma > 1 : 밝은 부분을 더 눌러서 전체적으로 어두워짐
#   - 이 코드는 "같은 사진에 여러 gamma 값을 적용했을 때 어떻게 보이는지"
#     한 번에 비교하기 위해 사용됩니다.
# ---------------------------------------------------------

# 주인님 PC 환경에 맞게 경로를 바꿔야 할 수 있습니다.
img = cv.imread('C:/cv_workspace/data/soccer.jpg')  # 축구장 이미지 불러오기
# 보기 좋게 1/4 크기로 축소 (원본이 크면 화면에 다 안 나올 수 있어서 줄임)
img = cv.resize(img, dsize=(0, 0), fx=0.25, fy=0.25)

def gamma_correction(f, gamma=1.0):
    """
    감마 보정을 실제로 수행하는 함수입니다.

    매개변수:
        f      : 입력 영상 (0~255 범위의 uint8 타입 배열)
        gamma  : 감마 계수 (0.5, 0.75, 1.0, 2.0, 3.0 등 사용 가능)
    반환값:
        감마 보정된 영상 (uint8 타입)

    사용 예시:
        bright = gamma_correction(img, 0.5)  # 어둠을 많이 밝게
        dark   = gamma_correction(img, 2.0)  # 전체를 더 어둡게
    """
    # f는 0~255 정수인데, 실수 연산을 하기 위해 0~1 사이 실수로 바꿔 준다.
    f1 = f / 255.0
    # f1 ** gamma : 각 픽셀을 gamma 제곱해 줌
    # 0~1 사이 값이므로, 다시 0~255로 되돌릴 때 255를 곱해줌
    return np.uint8(255 * (f1 ** gamma))

# 여러 gamma 값을 한 번에 비교하기 위해
#  다섯 장의 감마 보정 이미지를 가로로 이어 붙입니다.
gamma_concat = np.hstack([
    gamma_correction(img, 0.5),   # gamma = 0.5 → 그림이 많이 밝아짐
    gamma_correction(img, 0.75),  # gamma = 0.75 → 조금 밝아짐
    gamma_correction(img, 1.0),   # gamma = 1.0  → 거의 원본과 동일
    gamma_correction(img, 2.0),   # gamma = 2.0  → 조금 어두워짐
    gamma_correction(img, 3.0)    # gamma = 3.0  → 많이 어두워짐
])

# 윈도우 제목에 어떤 실험인지 적어주면 나중에 다시 봐도 이해하기 쉽습니다.
cv.imshow('9week - Gamma correction (0.5, 0.75, 1.0, 2.0, 3.0)', gamma_concat)
cv.waitKey()           # 키보드를 누를 때까지 창을 유지
cv.destroyAllWindows() # 열려 있는 모든 OpenCV 창 닫기


# ---------------------------------------------------------
# [2] 가우시안 블러 + 엠보싱 필터
#   - 블러(Blur):
#       * 사진의 "흐릿한 버전"을 만드는 것
#       * 노이즈(잡음)를 줄이고 싶을 때, 또는 배경을 흐리게 만들고 싶을 때
#   - 엠보싱(Emboss):
#       * 동전처럼 튀어나온 느낌, 양각/음각 느낌을 주는 필터
#       * 회색 계열 텍스처를 만드는 데 많이 사용
#   - 이 코드는 "여러 크기의 블러와 엠보싱 필터를 적용했을 때
#     결과가 어떻게 달라지는지 확인"하는 실험입니다.
# ---------------------------------------------------------

img = cv.imread('C:/cv_workspace/data/soccer.jpg')
img = cv.resize(img, dsize=(0, 0), fx=0.4, fy=0.4)  # 조금만 줄여서 사용
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)          # 컬러 → 흑백으로 변환

# 영상 위에 'soccer'라는 글자를 흰색으로 써 넣습니다.
# 나중에 블러와 필터를 적용했을 때 글자가 어떻게 변하는지 보기 위함입니다.
cv.putText(gray, 'soccer', (10, 20),
           cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

cv.imshow('9week - Original gray', gray)

# 서로 다른 커널 크기의 가우시안 블러 적용
#   - (5,5), (9,9), (15,15) → 숫자가 커질수록 더 크게 주변을 평균내서 "더 흐릿"
blur_stack = np.hstack([
    cv.GaussianBlur(gray, (5, 5), 0.0),   # 작은 블러 (조금만 흐릿)
    cv.GaussianBlur(gray, (9, 9), 0.0),   # 중간 정도 블러
    cv.GaussianBlur(gray, (15, 15), 0.0)  # 큰 블러 (많이 흐릿)
])
cv.imshow('9week - Gaussian Smooth (5, 9, 15)', blur_stack)

# 엠보싱 커널
#   - 왼쪽 위 픽셀(-1)과 오른쪽 아래 픽셀(+1)의 차이를 강조
#   - 이 커널을 회색 영상에 적용하면, 경계가 튀어나온 느낌을 줌
emboss_kernel = np.array([
    [-1.0, 0.0, 0.0],
    [ 0.0, 0.0, 0.0],
    [ 0.0, 0.0, 1.0]
])

# filter2D 연산에서 중간 계산 값이 0~255를 넘어갈 수 있어서
# 안전하게 int16(더 큰 범위를 표현할 수 있는 정수)로 바꿔 줍니다.
gray16 = np.int16(gray)

# 엠보싱 필터 적용
#  - filter2D: 커널을 사용해서 영상 전체에 합성곱(convolution)을 수행
#  - + 128: 결과가 -값도 나올 수 있으므로 회색(128)을 기준으로 가운데 맞추기
emboss_float = cv.filter2D(gray16, -1, emboss_kernel) + 128

# 결과 값이 0 미만, 255 초과인 경우를 잘라내고
# 0~255 사이로 맞춘 후 uint8(이미지용 타입)로 변환
emboss = np.uint8(np.clip(emboss_float, 0, 255))

# 아래 두 개는 "잘못된 처리 예시"를 보여 주기 위한 코드입니다.
# 굳이 따라 쓰지는 않아도 되지만, 왜 clip이 필요하고
# 왜 자료형을 신경 써야 하는지 이해하는 데 도움이 됩니다.

# 클리핑 없이 바로 uint8로 바꾸면, 0 미만/255 초과 값이 돌아가(overflow) 버림
emboss_bad = np.uint8(cv.filter2D(gray16, -1, emboss_kernel) + 128)
# 애초에 gray를 int16으로 바꾸지 않고 바로 필터를 쓰면 더 이상한 결과가 나올 수 있음
emboss_worse = cv.filter2D(gray, -1, emboss_kernel)

cv.imshow('9week - Emboss (correct)', emboss)
cv.imshow('9week - Emboss_bad (overflow 가능)', emboss_bad)
cv.imshow('9week - Emboss_worse (직접 uint8에 필터)', emboss_worse)

cv.waitKey()
cv.destroyAllWindows()


# ---------------------------------------------------------
# [3] 보간법(Interpolation)에 따른 확대 차이
#   - 언제 쓰나?
#       * 이미지를 확대하거나 축소할 때 "빈 픽셀을 어떻게 채울지" 정해야 함
#   - 대표적인 방법:
#       * INTER_NEAREST  : 가장 가까운 픽셀 값만 가져옴 → 계단처럼 보임(픽셀 아트에 좋음)
#       * INTER_LINEAR   : 주변 4개 픽셀을 섞어서 부드럽게 만듦 → 기본, 보통 사진
#       * INTER_CUBIC    : 주변 16개 픽셀을 이용, 더 부드럽게 → 계산은 더 느리지만 퀄리티 ↑
#   - 이 코드는 "같은 영역을 세 보간법으로 확대했을 때 차이"를 보여 줍니다.
# ---------------------------------------------------------

img = cv.imread('C:/cv_workspace/data/rose.png')

# 관심 영역(ROI: Region Of Interest)을 잘라냅니다.
# 행(세로): 250~349, 열(가로): 170~269 구간의 사각형 부분만 잘라서 patch로 사용
patch = img[250:350, 170:270, :]

# 원본 이미지에 우리가 자른 부분이 어디인지 붉은 사각형으로 표시
img_rect = cv.rectangle(img.copy(), (170, 250), (270, 350), (255, 0, 0), 3)

# 세 가지 보간법으로 패치를 5배 확대
patch_nearest = cv.resize(patch, dsize=(0, 0), fx=5, fy=5,
                          interpolation=cv.INTER_NEAREST)
patch_linear = cv.resize(patch, dsize=(0, 0), fx=5, fy=5,
                         interpolation=cv.INTER_LINEAR)
patch_cubic = cv.resize(patch, dsize=(0, 0), fx=5, fy=5,
                        interpolation=cv.INTER_CUBIC)

cv.imshow('9week - Original with ROI', img_rect)
cv.imshow('9week - Resize NEAREST (계단 느낌)', patch_nearest)
cv.imshow('9week - Resize BILINEAR (보통)', patch_linear)
cv.imshow('9week - Resize BICUBIC (부드러움)', patch_cubic)

cv.waitKey()
cv.destroyAllWindows()


############################################################
# 10주차 - 엣지와 영역 검출
#   - 엣지(Sobel, Canny)
#   - 외곽선(Contour)
#   - Hough로 원 찾기
#   - SLIC 슈퍼픽셀
#   - Normalized cut (정규화 절단)
#   - 말(horse) 외곽선 기하학적 분석
############################################################
import cv2 as cv
import numpy as np
import skimage
from skimage import graph, segmentation
import time

# ---------------------------------------------------------
# [1] Sobel 에지 검출
#   - 이미지에서 "경계(밝기가 확 변하는 부분)"를 찾고 싶을 때 사용
#   - x 방향, y 방향으로 각각 미분해서 기울기를 구함
# ---------------------------------------------------------

img = cv.imread('C:/cv_workspace/data/soccer.jpg')
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  # 에지 검출은 보통 흑백으로 함

# x방향으로 미분 (dx=1, dy=0) → 세로 방향 에지가 강하게 나옴
grad_x = cv.Sobel(gray, cv.CV_32F, 1, 0, ksize=3)
# y방향으로 미분 (dx=0, dy=1) → 가로 방향 에지가 강하게 나옴
grad_y = cv.Sobel(gray, cv.CV_32F, 0, 1, ksize=3)

# 실수/음수 값이 포함된 결과를 "0~255 양수"로 바꿔주기 위해
# 절대값을 취하고 타입을 8비트로 바꾸는 함수
sobel_x = cv.convertScaleAbs(grad_x)
sobel_y = cv.convertScaleAbs(grad_y)

# x 방향과 y 방향 에지를 반반 비율(0.5, 0.5)로 섞어서
# 전체적인 에지 강도(엣지 크기)를 만든다.
edge_strength = cv.addWeighted(sobel_x, 0.5, sobel_y, 0.5, 0)

cv.imshow('10week - Gray', gray)
cv.imshow('10week - Sobel X', sobel_x)
cv.imshow('10week - Sobel Y', sobel_y)
cv.imshow('10week - Sobel Edge Strength', edge_strength)
cv.waitKey()
cv.destroyAllWindows()


# ---------------------------------------------------------
# [2] Canny 에지 검출
#   - 가장 많이 쓰이는 에지 검출 알고리즘 중 하나
#   - 노이즈 제거 + 그라디언트 계산 + 히스테리시스 임계값 등 여러 단계가 합쳐진 방식
# ---------------------------------------------------------

img = cv.imread('C:/cv_workspace/data/soccer.jpg')
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

# (50, 150)처럼 낮은 임계값을 쓰면 에지가 더 많이 검출됨(노이즈도 포함)
canny1 = cv.Canny(gray, 50, 150)
# (100, 200)처럼 값을 올리면 에지가 덜 나오지만 더 깔끔해짐
canny2 = cv.Canny(gray, 100, 200)

cv.imshow('10week - Gray', gray)
cv.imshow('10week - Canny (50,150)', canny1)
cv.imshow('10week - Canny (100,200)', canny2)
cv.waitKey()
cv.destroyAllWindows()


# ---------------------------------------------------------
# [3] Contour(외곽선) 검출 + 길이 필터링
#   - Canny로 얻은 에지에서 "연결된 선"을 찾아서
#     각 객체의 윤곽선을 뽑아내는 기능
#   - 길이가 짧은 contour는 노이즈일 수 있어서 버리기도 함
# ---------------------------------------------------------

img = cv.imread('C:/cv_workspace/data/soccer.jpg')
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
canny = cv.Canny(gray, 100, 200)   # 에지 영상

# contours: 외곽선 리스트, 각각의 외곽선은 점들(좌표)의 집합
# hierarchy: 외곽선들의 포함 관계 정보 (여기선 크게 중요하지 않음)
contours, hierarchy = cv.findContours(
    canny, cv.RETR_LIST, cv.CHAIN_APPROX_NONE
)

# 너무 짧은 contour는 노이즈일 가능성이 높아서 제거
long_contours = []
for c in contours:
    # c.shape[0] : contour를 구성하는 점의 개수
    if c.shape[0] > 100:
        long_contours.append(c)

# 원본에 필터링된 길이 긴 외곽선만 초록색으로 그림
img_contour = img.copy()
cv.drawContours(img_contour, long_contours, -1, (0, 255, 0), 3)

cv.imshow('10week - Canny', canny)
cv.imshow('10week - Selected Contours (len>100)', img_contour)
cv.waitKey()
cv.destroyAllWindows()


# ---------------------------------------------------------
# [4] Hough Circle 변환으로 원 검출
#   - 동전, 볼, 눈동자, 사과 등 "원 모양" 물체를 자동으로 찾고 싶을 때 사용
# ---------------------------------------------------------

img = cv.imread('C:/cv_workspace/data/apples.jpg')
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

# Hough 원 검출 함수
circles = cv.HoughCircles(
    gray,
    cv.HOUGH_GRADIENT,   # 알고리즘 종류
    dp=1,                # 누적기 해상도 비율 (1이면 입력 크기 그대로)
    minDist=200,         # 원 중심끼리의 최소 거리
    param1=150,          # 내부적으로 쓰이는 Canny high threshold
    param2=20,           # 원으로 인정할 최소 누적값 (낮으면 더 많이 검출)
    minRadius=50,        # 최소 반지름
    maxRadius=120        # 최대 반지름
)

img_circle = img.copy()
# circles가 None이 아닌 경우에만 반복 (검출 실패할 수도 있으므로)
if circles is not None:
    for c in circles[0]:
        center = (int(c[0]), int(c[1]))  # 원 중심
        radius = int(c[2])               # 반지름
        # 빨간색 원을 그림
        cv.circle(img_circle, center, radius, (255, 0, 0), 2)

cv.imshow('10week - Detected circles', img_circle)
cv.waitKey()
cv.destroyAllWindows()


# ---------------------------------------------------------
# [5] SLIC Superpixel 분할
#   - "픽셀 하나하나" 대신 "비슷한 픽셀끼리 묶은 작은 영역(슈퍼픽셀)" 단위로
#     이미지를 나누는 방법
#   - 나중에 세그멘테이션이나 물체 인식의 전처리 작업에 많이 사용
# ---------------------------------------------------------

coffee = skimage.data.coffee()  # skimage에서 제공하는 예제 이미지 (RGB)
cv.imshow('10week - Coffee image', cv.cvtColor(coffee, cv.COLOR_RGB2BGR))

# compactness:
#   - 색깔 vs 위치의 중요도를 조절하는 값
#   - 값이 커질수록 "위치"를 더 중요하게 보고, 더 네모/동그란 모양의 블록이 생김
slic1 = segmentation.slic(coffee, compactness=20, n_segments=600)
slic2 = segmentation.slic(coffee, compactness=40, n_segments=600)

# mark_boundaries: 각 슈퍼픽셀 경계를 색깔로 표시해 줌
sp_img1 = segmentation.mark_boundaries(coffee, slic1)
sp_img2 = segmentation.mark_boundaries(coffee, slic2)

# skimage 이미지는 0~1 실수라서, OpenCV로 보기 위해 0~255로 스케일업
sp_img1 = np.uint8(sp_img1 * 255.0)
sp_img2 = np.uint8(sp_img2 * 255.0)

cv.imshow('10week - Superpixels (compact=20)',
          cv.cvtColor(sp_img1, cv.COLOR_RGB2BGR))
cv.imshow('10week - Superpixels (compact=40)',
          cv.cvtColor(sp_img2, cv.COLOR_RGB2BGR))

cv.waitKey()
cv.destroyAllWindows()


# ---------------------------------------------------------
# [6] Normalized Cut(정규화 절단) 기반 영역 분할
#   - 그래프 이론을 이용해서 이미지를 "비슷한 영역끼리" 분할하는 방법
#   - 계산량이 많아서 큰 이미지에는 무겁지만,
#     영상 분할의 이론적 기준으로 자주 등장
# ---------------------------------------------------------

coffee = skimage.data.coffee()

start = time.time()  # 시간 측정 시작

# 1단계: SLIC으로 슈퍼픽셀을 먼저 만든다.
slic = segmentation.slic(coffee, compactness=30, n_segments=600)

# 2단계: 각 슈퍼픽셀을 노드로 하는 RAG(Region Adjacency Graph)를 생성
#        → 서로 이웃한 영역끼리 얼마나 비슷한지(색깔) 점수로 표현
g = graph.rag_mean_color(coffee, slic, mode='similarity')

# 3단계: RAG 그래프에 Normalized cut 알고리즘을 적용하여 분할
ncut = graph.cut_normalized(slic, g)

print(coffee.shape, '영상을 분할하는데',
      time.time() - start, '초 소요')

# 분할 결과의 경계를 원본 위에 표시
marking = segmentation.mark_boundaries(coffee, ncut)
ncut_coffee = np.uint8(marking * 255.0)

cv.imshow('10week - Normalized cut',
          cv.cvtColor(ncut_coffee, cv.COLOR_RGB2BGR))
cv.waitKey()
cv.destroyAllWindows()


# ---------------------------------------------------------
# [7] 말(horse) 바이너리 영상에서 Contour + Convex Hull
#   - 이진(흑/백) 이미지에서 말 모양의 외곽선을 찾고,
#     면적, 중심, 둘레, 둥근 정도(roundness)를 계산
#   - 그리고 contour를 직선으로 근사한 것과
#     볼록 헐(Convex Hull)을 함께 그려 보는 예제
# ---------------------------------------------------------

orig = skimage.data.horse()          # horse: True/False 이진 이미지
# 말 영역(True)을 흰색(255) 아니라 "검은 실루엣"으로 만들기 위해 반전
img_horse = 255 - np.uint8(orig) * 255
cv.imshow('10week - Horse binary', img_horse)

# 외곽선 검출: RETR_EXTERNAL → 가장 바깥쪽 contour만 찾음
contours, hierarchy = cv.findContours(
    img_horse, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE
)

# 외곽선을 색깔로 표시하기 위해 GRAY → BGR 컬러로 변환
horse_contour_img = cv.cvtColor(img_horse, cv.COLOR_GRAY2BGR)
# 모든 contour를 자홍색(255,0,255)으로 그림
cv.drawContours(horse_contour_img, contours, -1, (255, 0, 255), 2)
cv.imshow('10week - Horse with contour', horse_contour_img)

# horse 예제는 말 하나만 있으므로 contours[0]만 사용
contour = contours[0]

# 모멘트 m을 이용하면 면적, 중심, 관성 모멘트 등 여러 정보를 얻을 수 있음
m = cv.moments(contour)
area = cv.contourArea(contour)               # 말의 전체 면적(픽셀 수)
cx, cy = m['m10'] / m['m00'], m['m01'] / m['m00']  # 무게중심(중심 좌표)
perimeter = cv.arcLength(contour, True)      # 둘레 길이
roundness = (4.0 * np.pi * area) / (perimeter * perimeter)
# roundness 값이 1에 가까울수록 '원'에 가까운 모양, 작으면 길쭉하거나 찌그러진 모양

print('Horse area =', area)
print('center = (', cx, ',', cy, ')')
print('perimeter =', perimeter)
print('roundness =', roundness)

# 직선 근사 및 볼록 헐을 그릴 새 이미지
horse_shape_img = cv.cvtColor(img_horse, cv.COLOR_GRAY2BGR)

# 외곽선을 직선 조각들로 근사 (epsilon=8 픽셀 오차 허용)
#  → 너무 세밀한 굴곡을 무시하고 대략적인 모양만 본다고 생각하면 됨
contour_approx = cv.approxPolyDP(contour, 8, True)
cv.drawContours(horse_shape_img, [contour_approx], -1, (0, 255, 0), 2)

# 볼록 헐(Convex Hull) 계산: 말 전체를 둘러싸는 가장 작은 볼록 다각형
hull = cv.convexHull(contour)
hull = hull.reshape(1, hull.shape[0], hull.shape[2])
cv.drawContours(horse_shape_img, hull, -1, (0, 0, 255), 2)

cv.imshow('10week - Horse with line segments and convex hull', horse_shape_img)
cv.waitKey()
cv.destroyAllWindows()

############################################################
# 11주차 - 인공신경망 (MLP, 옵티마이저 비교, 깊은 MLP, 이미지 예측)
############################################################
import numpy as np
import tensorflow as tf
import tensorflow.keras.datasets as ds
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import SGD, Adam
import matplotlib.pyplot as plt
import cv2

# ---------------------------------------------------------
# [11-1] 기본 MLP로 MNIST 숫자 분류
#   - 이 코드는 "손글씨 숫자(MNIST)를 0~9로 분류"하는
#     가장 기본적인 다층 퍼셉트론(MLP) 예제를 실행할 때 사용됩니다.
#   - 결과로 "테스트 정확도(%)"를 출력합니다.
# ---------------------------------------------------------

# 1) MNIST 데이터 불러오기
#    - x: 이미지 (28x28)
#    - y: 정답 숫자 (0~9)
(x_train, y_train), (x_test, y_test) = ds.mnist.load_data()

# 2) 입력 데이터를 네트워크가 쓰기 좋은 형태로 바꾸기
#    - 28x28 이미지를 784(=28*28) 길이의 1차원 벡터로 펼침
#    - /255.0 해서 픽셀값을 0~1 사이 실수로 정규화
x_train = x_train.reshape(60000, 784).astype(np.float32) / 255.0
x_test  = x_test.reshape(10000, 784).astype(np.float32) / 255.0

# 3) 정답 레이블을 원-핫 인코딩으로 바꾸기
#    - 예: 숫자 3 → [0,0,0,1,0,0,0,0,0,0]
y_train_oh = tf.keras.utils.to_categorical(y_train, 10)
y_test_oh  = tf.keras.utils.to_categorical(y_test, 10)

# 4) MLP 모델 만들기
#    - 입력: 784차원
#    - 은닉층: 512 노드, 활성함수 tanh
#    - 출력층: 10 노드, 활성함수 softmax (각 숫자에 대한 확률)
mlp = Sequential()
mlp.add(Dense(units=512, activation='tanh', input_shape=(784,)))
mlp.add(Dense(units=10, activation='softmax'))

# 5) 학습 방법(손실함수, 옵티마이저, 지표) 설정
#    - loss='MSE' : 여기서는 예제로 평균제곱오차 사용 (원래는 crossentropy가 더 일반적)
#    - optimizer=SGD : 확률적 경사 하강법, learning_rate=0.01
#    - metrics=['accuracy'] : 정확도도 같이 계산
mlp.compile(
    loss='MSE',
    optimizer=SGD(learning_rate=0.01),
    metrics=['accuracy']
)

# 6) 실제 학습 실행
#    - batch_size=128 : 한 번에 128장씩 묶어서 학습
#    - epochs=20      : 데이터 전체를 20번 반복해서 학습
#    - validation_data=(x_test, y_test_oh) : 테스트 데이터를 검증용으로 같이 사용
history_mlp = mlp.fit(
    x_train, y_train_oh,
    batch_size=128,
    epochs=20,
    validation_data=(x_test, y_test_oh),
    verbose=2
)

# 7) 테스트 데이터로 최종 정확도 측정
test_loss, test_acc = mlp.evaluate(x_test, y_test_oh, verbose=0)
print('[11주차 기본 MLP+SGD] 테스트 정확도 =', test_acc * 100, '%')


# ---------------------------------------------------------
# [11-2] 학습된 MLP로 "내가 그린 숫자 이미지" 예측
#   - 이 코드는 "number.png" 파일 속 숫자가 몇인지
#     주인님의 MLP 모델에게 물어보고 싶은 경우에 사용됩니다.
# ---------------------------------------------------------

# 1) 이미지를 흑백으로 읽기
img = cv2.imread('C:/cv_workspace/data/number.png',
                 cv2.IMREAD_GRAYSCALE)

# 2) MNIST와 똑같이 28x28 크기로 맞추기
img = cv2.resize(img, (28, 28))

# 3) 0~255 → 0~1로 정규화
img_norm = img / 255.0

# 4) (28,28) → (1,784) 모양으로 펼치기 (배치 1개)
x_input = img_norm.reshape(1, 784)

# 5) 예측 수행
pred = mlp.predict(x_input)
# 6) 확률이 가장 큰 인덱스(0~9)가 예측된 숫자
pred_label = np.argmax(pred)
print('[11주차 MLP] number.png 예측 숫자 =', pred_label)


# ---------------------------------------------------------
# [11-3] 같은 구조에서 SGD vs Adam 옵티마이저 비교
#   - 이 코드는 "옵티마이저를 바꾸면 학습 속도/정확도가 어떻게 달라지는지"
#     확인하고 싶을 때 사용됩니다.
#   - 결과로 학습/검증 정확도 그래프를 보여줍니다.
# ---------------------------------------------------------

# 데이터는 위에서 준비한 것 재사용 (x_train, y_train_oh, x_test, y_test_oh)

# --- SGD 버전 MLP ---
mlp_sgd = Sequential()
mlp_sgd.add(Dense(units=512, activation='tanh', input_shape=(784,)))
mlp_sgd.add(Dense(units=10, activation='softmax'))

mlp_sgd.compile(
    loss='MSE',
    optimizer=SGD(learning_rate=0.01),
    metrics=['accuracy']
)

hist_sgd = mlp_sgd.fit(
    x_train, y_train_oh,
    batch_size=128,
    epochs=20,
    validation_data=(x_test, y_test_oh),
    verbose=0  # 조용히 학습
)
sgd_acc = mlp_sgd.evaluate(x_test, y_test_oh, verbose=0)[1]
print('[11주차] SGD 최종 정확도 =', sgd_acc * 100, '%')

# --- Adam 버전 MLP ---
mlp_adam = Sequential()
mlp_adam.add(Dense(units=512, activation='tanh', input_shape=(784,)))
mlp_adam.add(Dense(units=10, activation='softmax'))

mlp_adam.compile(
    loss='MSE',
    optimizer=Adam(learning_rate=0.001),
    metrics=['accuracy']
)

hist_adam = mlp_adam.fit(
    x_train, y_train_oh,
    batch_size=128,
    epochs=20,
    validation_data=(x_test, y_test_oh),
    verbose=0
)
adam_acc = mlp_adam.evaluate(x_test, y_test_oh, verbose=0)[1]
print('[11주차] Adam 최종 정확도 =', adam_acc * 100, '%')

# --- 학습 곡선 비교 그래프 ---
plt.figure()
plt.plot(hist_sgd.history['accuracy'],     'r--', label='SGD train')
plt.plot(hist_sgd.history['val_accuracy'], 'r',   label='SGD val')
plt.plot(hist_adam.history['accuracy'],    'b--', label='Adam train')
plt.plot(hist_adam.history['val_accuracy'],'b',   label='Adam val')
plt.title('11주차 - SGD vs Adam 정확도 비교')
plt.xlabel('epoch')
plt.ylabel('accuracy')
plt.ylim(0.7, 1.0)
plt.grid()
plt.legend()
plt.show()


# ---------------------------------------------------------
# [11-4] 더 깊은 MLP (Deep MLP)로 정확도 향상 + 그래프
#   - 이 코드는 은닉층을 여러 개로 늘린 "깊은 신경망"을 학습하고,
#     정확도/손실 곡선을 그려 보고 싶은 때 사용됩니다.
# ---------------------------------------------------------

# 1) 데이터 다시 준비 (혹시 위에서 메모리 정리했을 수도 있으니)
(x_train, y_train), (x_test, y_test) = ds.mnist.load_data()
x_train = x_train.reshape(60000, 784).astype(np.float32) / 255.0
x_test  = x_test.reshape(10000, 784).astype(np.float32) / 255.0
y_train_oh = tf.keras.utils.to_categorical(y_train, 10)
y_test_oh  = tf.keras.utils.to_categorical(y_test, 10)

# 2) 깊은 MLP 구조
dmlp = Sequential()
dmlp.add(Dense(units=1024, activation='relu', input_shape=(784,)))
dmlp.add(Dense(units=512, activation='relu'))
dmlp.add(Dense(units=512, activation='relu'))
dmlp.add(Dense(units=10, activation='softmax'))

# 3) 분류 문제에 더 자주 쓰이는 손실: categorical_crossentropy
dmlp.compile(
    loss='categorical_crossentropy',
    optimizer=Adam(learning_rate=0.0001),
    metrics=['accuracy']
)

# 4) 학습
hist_dmlp = dmlp.fit(
    x_train, y_train_oh,
    batch_size=128,
    epochs=30,
    validation_data=(x_test, y_test_oh),
    verbose=0
)

# 5) 최종 정확도 출력
test_acc_dmlp = dmlp.evaluate(x_test, y_test_oh, verbose=0)[1]
print('[11주차 Deep MLP] 테스트 정확도 =', test_acc_dmlp * 100, '%')

# 6) 정확도/손실 그래프
plt.figure()
plt.plot(hist_dmlp.history['accuracy'], label='train acc')
plt.plot(hist_dmlp.history['val_accuracy'], label='val acc')
plt.title('11주차 - Deep MLP Accuracy')
plt.xlabel('epoch')
plt.ylabel('accuracy')
plt.legend()
plt.grid()
plt.show()

plt.figure()
plt.plot(hist_dmlp.history['loss'], label='train loss')
plt.plot(hist_dmlp.history['val_loss'], label='val loss')
plt.title('11주차 - Deep MLP Loss')
plt.xlabel('epoch')
plt.ylabel('loss')
plt.legend()
plt.grid()
plt.show()

# 7) 학습된 모델 저장 (시험·과제에서 "학습된 모델 불러오기" 문제에 사용 가능)
dmlp.save('dmlp_trained.h5')

# 8) number.png에 대해 Deep MLP로 예측
img = cv2.imread('C:/cv_workspace/data/number.png',
                 cv2.IMREAD_GRAYSCALE)
img = cv2.resize(img, (28, 28))
img_norm = img / 255.0
x_input = img_norm.reshape(1, 784)
pred = dmlp.predict(x_input)
label = np.argmax(pred)
print('[11주차 Deep MLP] number.png 예측 숫자 =', label)


############################################################
# 12주차 - 합성곱 신경망(CNN) I (Fashion-MNIST)
############################################################
import keras
from sklearn.model_selection import train_test_split

# ---------------------------------------------------------
# [12-1] Fashion-MNIST에 CNN 적용 (기본 구조 + 조기 종료)
#   - 이 코드는 옷 이미지를 10가지 종류(티셔츠, 바지, 코트 등)로
#     분류하는 CNN을 학습하고, 학습/검증 손실 그래프를 그릴 때 사용됩니다.
# ---------------------------------------------------------

# 1) 데이터 불러오기
(train_input, train_target), (test_input, test_target) = \
    keras.datasets.fashion_mnist.load_data()

# 2) CNN 입력형태로 변환 + 정규화
#    - (N,28,28) → (N,28,28,1)
train_scaled = train_input.reshape(-1, 28, 28, 1) / 255.0
test_scaled  = test_input.reshape(-1, 28, 28, 1) / 255.0

# 3) 학습/검증 나누기
train_scaled, val_scaled, train_target, val_target = train_test_split(
    train_scaled, train_target,
    test_size=0.2,
    random_state=42
)

# 4) CNN 모델 구성
model = keras.Sequential()
model.add(keras.layers.Input(shape=(28, 28, 1)))
model.add(keras.layers.Conv2D(32, kernel_size=3,
                              activation='relu', padding='same'))
model.add(keras.layers.MaxPooling2D(2))
model.add(keras.layers.Conv2D(64, kernel_size=3,
                              activation='relu', padding='same'))
model.add(keras.layers.MaxPooling2D(2))
model.add(keras.layers.Flatten())
model.add(keras.layers.Dense(100, activation='relu'))
model.add(keras.layers.Dropout(0.4))
model.add(keras.layers.Dense(10, activation='softmax'))

model.summary()  # 층 구조 출력

# 5) 컴파일 (다중 분류 + accuracy)
model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# 6) 콜백 설정 (베스트 모델 저장 + 조기 종료)
checkpoint_cb = keras.callbacks.ModelCheckpoint(
    'best-cnn-model.keras',
    save_best_only=True
)
early_stopping_cb = keras.callbacks.EarlyStopping(
    patience=2,
    restore_best_weights=True
)

# 7) 학습 실행
history_cnn = model.fit(
    train_scaled, train_target,
    epochs=20,
    validation_data=(val_scaled, val_target),
    callbacks=[checkpoint_cb, early_stopping_cb]
)

# 8) 손실 곡선 시각화
plt.figure()
plt.plot(history_cnn.history['loss'], label='train loss')
plt.plot(history_cnn.history['val_loss'], label='val loss')
plt.xlabel('epoch')
plt.ylabel('loss')
plt.legend()
plt.grid()
plt.show()

# 9) 검증/테스트 정확도 출력
val_loss, val_acc = model.evaluate(val_scaled, val_target, verbose=0)
print('[12주차 CNN] 검증 정확도:', val_acc)
test_loss, test_acc = model.evaluate(test_scaled, test_target, verbose=0)
print('[12주차 CNN] 테스트 정확도:', test_acc)

# 10) 샘플 하나에 대한 클래스별 확률 막대그래프
preds = model.predict(val_scaled[0:1])
print('[12주차 CNN] 첫 번째 검증 샘플 softmax 출력:', preds)

plt.figure()
plt.bar(range(10), preds[0])
plt.xlabel('class index')
plt.ylabel('prob.')
plt.title('12주차 - Sample prediction probability')
plt.show()

classes = ['티셔츠', '바지', '스웨터', '드레스', '코트',
           '샌달', '셔츠', '스니커즈', '가방', '앵클 부츠']
print('[12주차 CNN] 예측 클래스 이름 =', classes[np.argmax(preds[0])])


# ---------------------------------------------------------
# [12-2] 합성곱층 필터(가중치) 시각화
#   - 이 코드는 학습된 첫 번째 Conv2D 레이어의 필터들이
#     어떤 모양을 하고 있는지 눈으로 보고 싶을 때 사용됩니다.
# ---------------------------------------------------------

conv = model.layers[0]              # 첫 번째 합성곱 층
conv_weights = conv.weights[0].numpy()  # (3,3,1,32) 모양 (3x3 필터 32개)
print('[12주차] conv1 weight shape =', conv_weights.shape)
print('  mean =', conv_weights.mean(), 'std =', conv_weights.std())

# 가중치 값 분포(히스토그램)
plt.figure()
plt.hist(conv_weights.reshape(-1, 1))
plt.xlabel('weight')
plt.ylabel('count')
plt.title('12주차 - Conv1 weight distribution')
plt.show()

# 필터 모양을 2행 16열로 펼쳐서 그림 (32개)
fig, axs = plt.subplots(2, 16, figsize=(15, 2))
for i in range(2):
    for j in range(16):
        axs[i, j].imshow(conv_weights[:, :, 0, i * 16 + j],
                         vmin=-0.5, vmax=0.5, cmap='gray')
        axs[i, j].axis('off')
plt.suptitle('12주차 - Learned Conv1 filters')
plt.show()


# ---------------------------------------------------------
# [12-3] 랜덤 초기 필터와 비교하기
#   - 이 코드는 아직 학습되지 않은 Conv2D 필터가
#     어떤 분포와 모양을 갖는지, 위 결과와 비교하기 위해 사용됩니다.
# ---------------------------------------------------------

no_training_model = keras.Sequential()
no_training_model.add(keras.layers.Input(shape=(28, 28, 1)))
no_training_model.add(
    keras.layers.Conv2D(32, kernel_size=3,
                        activation='relu', padding='same')
)
no_conv = no_training_model.layers[0]
no_weights = no_conv.weights[0].numpy()

print('[12주차] 랜덤 Conv1 weight shape =', no_weights.shape)
print('  mean =', no_weights.mean(), 'std =', no_weights.std())

plt.figure()
plt.hist(no_weights.reshape(-1, 1))
plt.xlabel('weight')
plt.ylabel('count')
plt.title('12주차 - Random Conv1 weight distribution')
plt.show()

fig, axs = plt.subplots(2, 16, figsize=(15, 2))
for i in range(2):
    for j in range(16):
        axs[i, j].imshow(no_weights[:, :, 0, i * 16 + j],
                         vmin=-0.5, vmax=0.5, cmap='gray')
        axs[i, j].axis('off')
plt.suptitle('12주차 - Random Conv1 filters')
plt.show()


# ---------------------------------------------------------
# [12-4] Feature map (특징 맵) 시각화
#   - 이 코드는 실제 이미지(예: ankle boot)를 넣었을 때,
#     1층/2층 합성곱에서 어떤 특징 맵이 나오는지 시각화할 때 사용됩니다.
# ---------------------------------------------------------

conv1_acti = keras.Model(model.inputs, model.layers[0].output)
conv2_acti = keras.Model(model.inputs, model.layers[2].output)

(train_input, train_target), _ = keras.datasets.fashion_mnist.load_data()
plt.figure()
plt.imshow(train_input[0], cmap='gray_r')
plt.title('Original image (index 0)')
plt.show()

ankle_boot = train_input[0:1].reshape(-1, 28, 28, 1) / 255.0

# 1층 feature map
feature_maps1 = conv1_acti.predict(ankle_boot)
print('[12주차] conv1 feature shape =', feature_maps1.shape)

fig, axs = plt.subplots(4, 8, figsize=(15, 8))
for i in range(4):
    for j in range(8):
        axs[i, j].imshow(feature_maps1[0, :, :, i * 8 + j], cmap='gray')
        axs[i, j].axis('off')
plt.suptitle('12주차 - Conv1 feature maps')
plt.show()

# 2층 feature map
feature_maps2 = conv2_acti.predict(ankle_boot)
print('[12주차] conv2 feature shape =', feature_maps2.shape)

fig, axs = plt.subplots(8, 8, figsize=(12, 12))
for i in range(8):
    for j in range(8):
        axs[i, j].imshow(feature_maps2[0, :, :, i * 8 + j], cmap='gray')
        axs[i, j].axis('off')
plt.suptitle('12주차 - Conv2 feature maps')
plt.show()


############################################################
# 13주차 - CNN II (LeNet, 데이터 증강, 사전학습 모델)
############################################################
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.resnet50 import (
    ResNet50, preprocess_input, decode_predictions
)

# ---------------------------------------------------------
# [13-1] LeNet-5 스타일 CNN으로 MNIST 분류
#   - 이 코드는 고전적인 LeNet 구조를 흉내 내어
#     MNIST 숫자를 분류하고 정확도를 확인할 때 사용됩니다.
# ---------------------------------------------------------

(x_train, y_train), (x_test, y_test) = ds.mnist.load_data()
x_train = x_train.reshape(60000, 28, 28, 1).astype(np.float32) / 255.0
x_test  = x_test.reshape(10000, 28, 28, 1).astype(np.float32) / 255.0
y_train_oh = tf.keras.utils.to_categorical(y_train, 10)
y_test_oh  = tf.keras.utils.to_categorical(y_test, 10)

cnn = Sequential()
cnn.add(Conv2D(6, (5, 5), padding='same',
               activation='relu', input_shape=(28, 28, 1)))
cnn.add(MaxPooling2D(pool_size=(2, 2), strides=2))
cnn.add(Conv2D(16, (5, 5), padding='valid', activation='relu'))
cnn.add(MaxPooling2D(pool_size=(2, 2), strides=2))
cnn.add(Conv2D(120, (5, 5), padding='valid', activation='relu'))
cnn.add(Flatten())
cnn.add(Dense(units=84, activation='relu'))
cnn.add(Dense(units=10, activation='softmax'))

cnn.compile(
    loss='categorical_crossentropy',
    optimizer=Adam(learning_rate=0.001),
    metrics=['accuracy']
)

hist_lenet = cnn.fit(
    x_train, y_train_oh,
    batch_size=128,
    epochs=20,
    validation_data=(x_test, y_test_oh),
    verbose=0
)

res = cnn.evaluate(x_test, y_test_oh, verbose=0)
print('[13주차 LeNet] 테스트 정확도 =', res[1] * 100, '%')


# ---------------------------------------------------------
# [13-2] CIFAR-10 데이터 증강 시각화
#   - 이 코드는 작은 컬러 이미지(CIFAR-10)를 불러와서
#     회전, 이동, 좌우반전 등의 증강 결과를 눈으로 확인할 때 사용됩니다.
# ---------------------------------------------------------

(x_train_c, y_train_c), _ = ds.cifar10.load_data()
x_train_c = x_train_c.astype('float32') / 255.0

# 처음 15장만 사용해서 원본 이미지 보기
x_small = x_train_c[0:15]
y_small = y_train_c[0:15]

class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer',
               'dog', 'frog', 'horse', 'ship', 'truck']

plt.figure(figsize=(20, 2))
plt.suptitle('13주차 - CIFAR-10 원본 15장')
for i in range(15):
    plt.subplot(1, 15, i + 1)
    plt.imshow(x_small[i])
    plt.xticks([]); plt.yticks([])
    plt.title(class_names[int(y_small[i])])
plt.show()

# 데이터 증강 설정
generator = ImageDataGenerator(
    rotation_range=20.0,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True
)
gen = generator.flow(x_small, y_small, batch_size=4)

# 증강된 이미지 3번 정도 보기
for trial in range(3):
    imgs, labels = next(gen)
    plt.figure(figsize=(8, 2.4))
    plt.suptitle(f'13주차 - Generator trial {trial + 1}')
    for i in range(4):
        plt.subplot(1, 4, i + 1)
        plt.imshow(imgs[i])
        plt.xticks([]); plt.yticks([])
        plt.title(class_names[int(labels[i])])
    plt.show()


# ---------------------------------------------------------
# [13-3] ResNet50 사전학습 모델로 이미지 분류
#   - 이 코드는 ImageNet으로 미리 학습된 ResNet50을 사용하여
#     rabbit.jpg 이미지가 무엇인지 상위 5개 후보와 확률을 보여 줍니다.
# ---------------------------------------------------------

model_resnet = ResNet50(weights='imagenet')

img = cv.imread('C:/cv_workspace/data/rabbit.jpg')
# ResNet 입력 크기(224x224)에 맞추기
img_resized = cv.resize(img, (224, 224))
x = np.reshape(img_resized, (1, 224, 224, 3))
# ResNet50 전처리 함수 적용 (평균 빼기, 채널 순서 조정 등)
x = preprocess_input(x)

preds = model_resnet.predict(x)
top5 = decode_predictions(preds, top=5)[0]
print('[13주차 ResNet] 예측 결과 top5 =', top5)

# 이미지 위에 top5 결과를 텍스트로 덧붙이기
img_show = img.copy()
for i in range(5):
    text = f'{top5[i][1]}: {top5[i][2]:.3f}'
    cv.putText(img_show, text,
               (10, 20 + 20 * i),
               cv.FONT_HERSHEY_SIMPLEX, 0.5,
               (255, 255, 255), 1)

cv.imshow('13주차 - ResNet50 Recognition', img_show)
cv.waitKey()
cv.destroyAllWindows()


############################################################
# 14주차 - YOLO를 이용한 객체 검출
############################################################
import sys

# ---------------------------------------------------------
# [14-1] YOLO v3로 정지 이미지에서 객체 검출
#   - 이 코드는 soccer.jpg 한 장에 대해
#     사람, 공, 차 같은 물체를 검출하고, 박스와 클래스 이름을 그릴 때 사용됩니다.
# ---------------------------------------------------------

path = 'C:/cv_workspace/data/'

def construct_yolo_v3():
    """
    이 함수는 YOLO v3 네트워크를 구성하고,
    출력 레이어 이름과 클래스 이름 리스트를 만들어 돌려줍니다.
    """
    # 클래스(80개) 이름 읽기
    with open(path + 'coco_names.txt', 'r') as f:
        class_names = [line.strip() for line in f.readlines()]

    # YOLOv3 구조/가중치 불러오기
    model = cv.dnn.readNet(path + 'yolov3.weights',
                           path + 'yolov3.cfg')
    layer_names = model.getLayerNames()
    # 출력 레이어 인덱스를 실제 이름으로 변환
    out_layers = [layer_names[i - 1]
                  for i in model.getUnconnectedOutLayers()]
    return model, out_layers, class_names


def yolo_detect(img, yolo_model, out_layers):
    """
    이 함수는 입력 이미지 한 장에 대해 YOLO를 돌려서
    최종적으로 남은 객체 박스 리스트를 반환합니다.

    반환 형식:
        [ [x1, y1, x2, y2, confidence, class_id],
          ... ]
    """
    height, width = img.shape[:2]

    # 이미지를 small(448x448)로 리사이즈 + 정규화해서 blob 생성
    blob = cv.dnn.blobFromImage(
        img, 1.0 / 256, (448, 448),
        (0, 0, 0), swapRB=True
    )
    yolo_model.setInput(blob)

    # YOLO의 3개 출력 레이어 결과 얻기
    outputs = yolo_model.forward(out_layers)

    boxes, confs, ids = [], [], []

    # 각 output 안에는 여러 bounding box 후보가 들어 있음
    for output in outputs:
        for vec85 in output:
            scores = vec85[5:]       # 각 클래스별 점수
            cid = np.argmax(scores)  # 점수가 가장 큰 클래스 번호
            confidence = scores[cid]

            # 0.5 이상의 신뢰도를 가진 박스만 사용
            if confidence > 0.5:
                centerx, centery = int(vec85[0] * width), int(vec85[1] * height)
                w, h = int(vec85[2] * width), int(vec85[3] * height)
                x, y = int(centerx - w / 2), int(centery - h / 2)

                boxes.append([x, y, x + w, y + h])
                confs.append(float(confidence))
                ids.append(cid)

    # NMS(Non-Max Suppression)으로 겹치는 박스 정리
    ind = cv.dnn.NMSBoxes(boxes, confs, 0.5, 0.4)

    objects = [boxes[i] + [confs[i]] + [ids[i]]
               for i in range(len(boxes)) if i in ind]
    return objects


model_yolo, out_layers, class_names = construct_yolo_v3()
colors = np.random.uniform(0, 255, size=(len(class_names), 3))

img = cv.imread(path + 'soccer.jpg')
if img is None:
    sys.exit('이미지 파일이 없습니다.')

results = yolo_detect(img, model_yolo, out_layers)

# 검출된 객체마다 박스와 텍스트 그리기
for x1, y1, x2, y2, conf, cid in results:
    text = f'{class_names[cid]} {conf:.3f}'
    cv.rectangle(img, (x1, y1), (x2, y2), colors[cid], 2)
    cv.putText(img, text, (x1, y1 + 20),
               cv.FONT_HERSHEY_PLAIN, 1.2, colors[cid], 2)

cv.imshow('14주차 - YOLOv3 Object Detection', img)
cv.waitKey()
cv.destroyAllWindows()


# ---------------------------------------------------------
# [14-2] YOLO v3로 웹캠 실시간 객체 검출 (옵션)
#   - 이 코드는 웹캠이 연결되어 있을 때,
#     카메라 화면에 보이는 물체들을 실시간으로 검출하고 싶을 때 사용됩니다.
# ---------------------------------------------------------

def yolo_detect_cam(frame, yolo_model, out_layers):
    """
    이 함수는 웹캠 프레임 한 장에 대해 YOLO를 돌리고
    최종 박스 리스트를 반환합니다. (정지 이미지 버전과 거의 동일)
    """
    h, w = frame.shape[:2]
    blob = cv.dnn.blobFromImage(
        frame, 1.0 / 256, (448, 448),
        (0, 0, 0), swapRB=True
    )
    yolo_model.setInput(blob)
    outputs = yolo_model.forward(out_layers)

    boxes, confs, ids = [], [], []
    for output in outputs:
        for vec85 in output:
            scores = vec85[5:]
            cid = np.argmax(scores)
            confidence = scores[cid]
            if confidence > 0.5:
                centerx, centery = int(vec85[0] * w), int(vec85[1] * h)
                bw, bh = int(vec85[2] * w), int(vec85[3] * h)
                x, y = int(centerx - bw / 2), int(centery - bh / 2)
                boxes.append([x, y, x + bw, y + bh])
                confs.append(float(confidence))
                ids.append(cid)

    ind = cv.dnn.NMSBoxes(boxes, confs, 0.5, 0.4)
    objects = [boxes[i] + [confs[i]] + [ids[i]]
               for i in range(len(boxes)) if i in ind]
    return objects

cap = cv.VideoCapture(0)
if not cap.isOpened():
    sys.exit('카메라를 열 수 없습니다.')

while True:
    ret, frame = cap.read()
    if not ret:
        break

    res = yolo_detect_cam(frame, model_yolo, out_layers)
    for x1, y1, x2, y2, conf, cid in res:
        text = f'{class_names[cid]} {conf:.2f}'
        cv.rectangle(frame, (x1, y1), (x2, y2), colors[cid], 2)
        cv.putText(frame, text, (x1, y1 + 20),
                   cv.FONT_HERSHEY_PLAIN, 1.0, colors[cid], 2)

    cv.imshow('14주차 - YOLOv3 Webcam', frame)
    # ESC(27)를 누르면 종료
    if cv.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv.destroyAllWindows()
