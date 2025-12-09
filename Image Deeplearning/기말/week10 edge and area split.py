"""
10주차 - 엣지와 영역 검출
=========================

이 파일은 OpenCV + scikit-image로 다음 기능을 연습할 때 사용해.

1) Sobel 에지 검출
   - 기울기 기반 엣지 (영상의 변화가 큰 부분 찾기)

2) Canny 에지 검출
   - 실무에서 가장 많이 쓰이는 엣지 검출기

3) Contour(외곽선) 찾기
   - 이진/에지 영상에서 물체 윤곽선을 벡터 형태로 얻고 싶을 때

4) Hough Circle (원 검출)
   - 동전, 눈동자, 사과처럼 "원" 모양 물체 찾기

5) SLIC Superpixel
   - 이미지를 작은 "조각(슈퍼픽셀)"으로 먼저 나눠서 영역 분할/객체 인식 전처리로 사용

6) Normalized Cut (정규화 절단)
   - 그래프 이론 기반의 영역 분할 알고리즘. 더 고급 세그멘테이션.
"""

import cv2 as cv
import numpy as np
import skimage
from skimage import graph, segmentation
import time

# 주인님 환경에 맞게 경로는 자유롭게 수정!


# ---------------------------------------------------
# 1. Sobel 에지 검출
# ---------------------------------------------------
img = cv.imread('C:/cv_workspace/data/soccer.jpg')
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

# x 방향 (세로 경계 강조), y 방향 (가로 경계 강조)
grad_x = cv.Sobel(gray, cv.CV_32F, 1, 0, ksize=3)
grad_y = cv.Sobel(gray, cv.CV_32F, 0, 1, ksize=3)

# 절대값을 취하고 8비트로 변환
sobel_x = cv.convertScaleAbs(grad_x)
sobel_y = cv.convertScaleAbs(grad_y)

# 두 방향을 합쳐 전체 에지 강도 계산
edge_strength = cv.addWeighted(sobel_x, 0.5, sobel_y, 0.5, 0)

cv.imshow('Gray', gray)
cv.imshow('Sobel X', sobel_x)
cv.imshow('Sobel Y', sobel_y)
cv.imshow('Sobel Edge Strength', edge_strength)
cv.waitKey()
cv.destroyAllWindows()


# ---------------------------------------------------
# 2. Canny 에지 검출
# ---------------------------------------------------
# ※ 사용 상황 예시:
#   - 후속 처리(컨투어, Hough 등) 전에 깔끔한 에지를 얻고 싶을 때
#   - 객체 경계, 도로 차선, 경계선 검출 등

img = cv.imread('C:/cv_workspace/data/soccer.jpg')
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

# (low, high) 임계값에 따라 잡음/엣지가 얼마나 남는지 달라짐
canny1 = cv.Canny(gray, 50, 150)
canny2 = cv.Canny(gray, 100, 200)

cv.imshow('Gray', gray)
cv.imshow('Canny (50,150)', canny1)
cv.imshow('Canny (100,200)', canny2)
cv.waitKey()
cv.destroyAllWindows()


# ---------------------------------------------------
# 3. Contour(외곽선) 검출 + 길이 필터링
# ---------------------------------------------------
# ※ 사용 상황 예시:
#   - 이진 영상에서 각 물체의 외곽선(윤곽)을 얻고 싶을 때
#   - 각 물체의 면적, 둘레, 모양 등을 계산하려고 할 때

img = cv.imread('C:/cv_workspace/data/soccer.jpg')
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

canny = cv.Canny(gray, 100, 200)

# RETR_LIST : 계층 구조 관계 없이 모든 외곽선
contours, hierarchy = cv.findContours(
    canny, cv.RETR_LIST, cv.CHAIN_APPROX_NONE
)

# 너무 짧은 곡선은 무시하고, 충분히 긴 것만 선택
long_contours = [c for c in contours if c.shape[0] > 100]

img_contour = img.copy()
cv.drawContours(img_contour, long_contours, -1, (0, 255, 0), 3)

cv.imshow('Canny', canny)
cv.imshow('Selected Contours (len>100)', img_contour)
cv.waitKey()
cv.destroyAllWindows()


# ---------------------------------------------------
# 4. Hough 원 변환으로 원형 물체(사과) 찾기
# ---------------------------------------------------
# ※ 사용 상황 예시:
#   - 동전 개수 세기, 눈동자 위치 찾기, 사과/공 같은 원형 물체 검출

img = cv.imread('C:/cv_workspace/data/apples.jpg')
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

# HoughCircles 파라미터는 데이터에 따라 조정 필요
circles = cv.HoughCircles(
    gray,
    cv.HOUGH_GRADIENT,
    1,          # dp : 해상도 스케일(1=그대로)
    200,        # minDist : 원 중심 사이의 최소 거리
    param1=150, # 내부 Canny high threshold
    param2=20,  # 원으로 판단하는 임계값 (크면 덜 검출)
    minRadius=50,
    maxRadius=120
)

img_circle = img.copy()
if circles is not None:
    for c in circles[0]:
        center = (int(c[0]), int(c[1]))
        radius = int(c[2])
        cv.circle(img_circle, center, radius, (255, 0, 0), 2)

cv.imshow('Detected circles', img_circle)
cv.waitKey()
cv.destroyAllWindows()


# ---------------------------------------------------
# 5. SLIC Superpixel 분할
# ---------------------------------------------------
# ※ 사용 상황 예시:
#   - 픽셀 단위 대신 "조각 단위"로 처리하고 싶을 때
#   - 세그멘테이션/객체 인식의 전처리로 자주 쓰임

coffee = skimage.data.coffee()  # 예제 컬러 이미지 (RGB)

cv.imshow('Coffee image', cv.cvtColor(coffee, cv.COLOR_RGB2BGR))

# compactness : 색 vs 위치 중요도 비율 (숫자 커질수록 위치 중요)
slic1 = segmentation.slic(coffee, compactness=20, n_segments=600)
slic2 = segmentation.slic(coffee, compactness=40, n_segments=600)

sp_img1 = segmentation.mark_boundaries(coffee, slic1)
sp_img2 = segmentation.mark_boundaries(coffee, slic2)

sp_img1 = np.uint8(sp_img1 * 255.0)
sp_img2 = np.uint8(sp_img2 * 255.0)

cv.imshow('Superpixels (compact=20)', cv.cvtColor(sp_img1, cv.COLOR_RGB2BGR))
cv.imshow('Superpixels (compact=40)', cv.cvtColor(sp_img2, cv.COLOR_RGB2BGR))

cv.waitKey()
cv.destroyAllWindows()


# ---------------------------------------------------
# 6. Normalized Cut으로 영역 분할
# ---------------------------------------------------
# ※ 사용 상황 예시:
#   - 색/위치를 모두 고려해서 "비슷한 영역"을 자동으로 잘라내고 싶을 때
#   - 계산량이 많아서, 직접 쓸 때는 보통 이미지 크기가 크지 않을 때 사용

coffee = skimage.data.coffee()

start = time.time()

# 1단계: SLIC으로 적당한 슈퍼픽셀 분할
slic = segmentation.slic(coffee, compactness=30, n_segments=600)

# 2단계: 각 슈퍼픽셀을 정점으로 하는 그래프 생성 (색 유사도 기반)
g = graph.rag_mean_color(coffee, slic, mode='similarity')

# 3단계: Normalized Cut으로 그래프 분할 → 영역 레이블 맵 얻기
ncut = graph.cut_normalized(slic, g)

print(coffee.shape, '영상을 분할하는데',
      time.time() - start, '초 소요')

# 영역 경계를 원본에 표시
marking = segmentation.mark_boundaries(coffee, ncut)
ncut_img = np.uint8(marking * 255.0)

cv.imshow('Normalized cut result', cv.cvtColor(ncut_img, cv.COLOR_RGB2BGR))
cv.waitKey()
cv.destroyAllWindows()
