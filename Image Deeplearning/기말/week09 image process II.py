"""
9주차 - 영상 처리 II
====================

이 파일은 OpenCV로 다음 3가지를 실습할 때 사용하는 예제 코드야.

1) 감마 보정 (Gamma Correction)
   - 사진이 너무 어둡거나, 밝은 부분/어두운 부분을 더 강조하고 싶을 때 사용.
   - 모니터 감마 보정, 사진 후보정 등에 많이 쓰임.

2) 블러 + 엠보싱 필터 (컨볼루션)
   - 블러 : 노이즈 제거, 배경 흐리기 등.
   - 엠보싱 : 양각/음각 느낌을 주는 필터. ‘엠보싱 효과 이미지’ 만들 때 사용.

3) 보간법(Interpolation)에 따른 확대 차이
   - 이미지를 확대할 때 어떤 알고리즘을 쓰느냐에 따라 결과가 달라짐.
   - NEAREST / BILINEAR / BICUBIC 비교.
"""

import cv2 as cv
import numpy as np

# ---------------------------------------------------
# 1. 감마 보정
# ---------------------------------------------------
# ※ 사용 상황 예시:
#   - 사진이 전체적으로 너무 어두워서 밝게 만들고 싶을 때
#   - 밝은 부분/어두운 부분을 다르게 강조하고 싶을 때
#   - "감마 값 < 1" 이면 밝게, "감마 값 > 1" 이면 어둡게 됨

# 주인님 PC에 맞게 경로 수정하기!
img = cv.imread('C:/cv_workspace/data/soccer.jpg')
img = cv.resize(img, dsize=(0, 0), fx=0.25, fy=0.25)  # 큰 이미지는 보기 좋게 축소

def gamma_correction(f, gamma=1.0):
    """
    f : 입력 영상 (0~255)
    gamma : 감마 계수
    리턴 : 감마 보정된 영상 (uint8)
    """
    # 0~255 → 0~1 로 정규화
    f1 = f / 255.0
    # 감마 적용 후 다시 0~255 범위로 되돌리기
    return np.uint8(255 * (f1 ** gamma))

# 여러 감마 값에 대한 결과를 한 줄로 붙여 보기
gc = np.hstack([
    gamma_correction(img, 0.5),   # 많이 밝게
    gamma_correction(img, 0.75),  # 조금 밝게
    gamma_correction(img, 1.0),   # 원본과 동일
    gamma_correction(img, 2.0),   # 조금 어둡게
    gamma_correction(img, 3.0)    # 많이 어둡게
])

cv.imshow('Gamma correction (0.5, 0.75, 1.0, 2.0, 3.0)', gc)
cv.waitKey()
cv.destroyAllWindows()


# ---------------------------------------------------
# 2. 가우시안 블러 + 엠보싱 필터
# ---------------------------------------------------
# ※ 사용 상황 예시:
#   - 블러 : 노이즈 제거, 박스 흐림, 배경 흐리게 하기 등
#   - 엠보싱 : 회색 톤의 입체감 있는 이미지 만들기, 예술 효과

img = cv.imread('C:/cv_workspace/data/soccer.jpg')
img = cv.resize(img, dsize=(0, 0), fx=0.4, fy=0.4)
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

cv.putText(gray, 'soccer', (10, 20),
           cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

cv.imshow('Original (gray)', gray)

# ---- 가우시안 블러 : 커널 크기에 따라 얼마나 흐려지는지 비교 ----
smooth = np.hstack([
    cv.GaussianBlur(gray, (5, 5), 0.0),   # 약하게 흐림
    cv.GaussianBlur(gray, (9, 9), 0.0),   # 중간
    cv.GaussianBlur(gray, (15, 15), 0.0)  # 많이 흐림
])
cv.imshow('Gaussian Smooth (5, 9, 15)', smooth)

# ---- 엠보싱 필터 정의 ----
# 왼쪽 위와 오른쪽 아래의 차이를 강조하는 필터
femboss = np.array([
    [-1.0, 0.0, 0.0],
    [ 0.0, 0.0, 0.0],
    [ 0.0, 0.0, 1.0]
])

# 필터 계산 시 값 범위가 -255~255 정도로 커질 수 있어서 16비트 형으로 변환
gray16 = np.int16(gray)

# 필터 적용 + 128을 더해 회색 기준(128) 주변으로 이동
emboss_float = cv.filter2D(gray16, -1, femboss) + 128

# 0~255 범위 밖으로 나간 값을 잘라내고 uint8로 캐스팅
emboss = np.uint8(np.clip(emboss_float, 0, 255))

cv.imshow('Emboss (correct)', emboss)

cv.waitKey()
cv.destroyAllWindows()


# ---------------------------------------------------
# 3. 보간법에 따른 확대 차이 (Nearest / Bilinear / Bicubic)
# ---------------------------------------------------
# ※ 사용 상황 예시:
#   - 이미지 확대/축소가 필요한 모든 상황
#   - 최근접 : 픽셀 아트를 크게 보는 등 "계단 느낌"을 일부러 살리고 싶을 때
#   - 선형/3차 : 일반 사진 확대(부드러운 결과 필요할 때)

img = cv.imread('C:/cv_workspace/data/rose.png')

# 관심 영역(꽃의 일부)을 잘라서 보간법만 비교
patch = img[250:350, 170:270, :]

# 원본에 빨간 사각형 표시해서 어디를 확대했는지 보여주기
img_rect = cv.rectangle(img.copy(), (170, 250), (270, 350), (255, 0, 0), 3)

# 각각 다른 보간법으로 5배 확대
patch_nearest = cv.resize(patch, dsize=None, fx=5, fy=5,
                          interpolation=cv.INTER_NEAREST)
patch_bilinear = cv.resize(patch, dsize=None, fx=5, fy=5,
                           interpolation=cv.INTER_LINEAR)
patch_bicubic = cv.resize(patch, dsize=None, fx=5, fy=5,
                          interpolation=cv.INTER_CUBIC)

cv.imshow('Original with ROI', img_rect)
cv.imshow('Nearest (계단 느낌)', patch_nearest)
cv.imshow('Bilinear (보통 사진 확대)', patch_bilinear)
cv.imshow('Bicubic (더 부드럽게)', patch_bicubic)

cv.waitKey()
cv.destroyAllWindows()
