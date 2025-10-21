# -*- coding: utf-8 -*-
"""
파일 이름: week07_ImageProcessing_annotated.py

무엇을 하나요?
- OpenCV로 이미지/동영상 불러오기, 화면에 보여주기, 저장하기
- 마우스/키보드 이벤트로 그리기
- 색상 채널/히스토그램/이진화(오츠), 감마보정, 히스토그램 평활화
- 블러/컨볼루션(엠보싱), 형태학적 연산(팽창/침식/열림/닫힘) 등

필요:
- pip install opencv-python matplotlib numpy
- 로컬 이미지/동영상 파일 경로를 내 PC에 맞게 수정하세요.
"""

import cv2 as cv
import sys
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------
# 1) 이미지 읽고 보여주기 + 픽셀 값 확인
# -------------------------------
img = cv.imread('C:/cv_workspace/data/soccer.jpg')  # 이미지 파일을 읽어요
if img is None:
    sys.exit('파일을 찾을 수 없습니다. (경로를 확인하세요)')

cv.imshow('Image Display', img)  # 윈도우 창에 이미지를 보여줌
cv.waitKey()                     # 키 입력이 올 때까지 대기
cv.destroyAllWindows()           # 열린 창 닫기

# 이미지 자료형/크기 확인 (참고용)
# type(img)        # <class 'numpy.ndarray'>
# img.shape        # (높이, 너비, 채널수) 예: (1080, 1920, 3)

# (0,0)과 (0,1) 위치 픽셀의 B,G,R 값을 출력
print(img[0, 0, 0], img[0, 0, 1], img[0, 0, 2])  # 예상: 0~255
print(img[0, 1, 0], img[0, 1, 1], img[0, 1, 2])

# -------------------------------
# 2) 그레이스케일 변환 + 리사이즈 + 파일 저장
# -------------------------------
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)             # 색->회색
gray_small = cv.resize(gray, dsize=(0,0), fx=0.5, fy=0.5)  # 절반 크기

cv.imwrite('soccer_gray.jpg', gray)         # 현재 폴더에 저장
cv.imwrite('soccer_gray_small.jpg', gray_small)
cv.imshow('Color image', img)
cv.imshow('Gray image', gray)
cv.imshow('Gray image small', gray_small)
cv.waitKey(); cv.destroyAllWindows()

# -------------------------------
# 3) 웹캠(카메라)에서 실시간 프레임 읽기
# -------------------------------
cap = cv.VideoCapture(0, cv.CAP_DSHOW)  # 0번 카메라 연결 시도(윈도우라면 CAP_DSHOW 추천)
if not cap.isOpened():
    sys.exit('카메라 연결 실패')

while True:
    ret, frame = cap.read()  # 한 프레임 읽기
    if not ret:
        print('프레임 획득 실패. 루프 종료')
        break
    cv.imshow('Video display', frame)
    key = cv.waitKey(1)
    if key == ord('q'):  # q 키를 누르면 종료
        break

cap.release()       # 카메라와 연결 해제
cv.destroyAllWindows()

# -------------------------------
# 4) 웹캠에서 프레임 모으기(c 키로 캡쳐) 후 옆으로 이어붙여 보기
# -------------------------------
cap = cv.VideoCapture(0, cv.CAP_DSHOW)
if not cap.isOpened():
    sys.exit('카메라 연결 실패')

frames = []
while True:
    ret, frame = cap.read()
    if not ret:
        print('프레임 획득 실패. 루프 종료')
        break
    cv.imshow('Video display', frame)
    key = cv.waitKey(1)
    if key == ord('c'):     # c를 누를 때마다 현재 프레임을 저장
        frames.append(frame)
    elif key == ord('q'):   # q면 종료
        break

cap.release(); cv.destroyAllWindows()

if len(frames) > 0:
    # 최대 3장까지 좌우로 이어붙여 한 장으로 보여줍니다.
    imgs = frames[0]
    for i in range(1, min(3, len(frames))):
        imgs = np.hstack((imgs, frames[i]))
    cv.imshow('collected images', imgs)
    cv.waitKey(); cv.destroyAllWindows()
else:
    print("[WARN] 수집된 프레임이 없습니다.")

# -------------------------------
# 5) 도형/텍스트 그리기
# -------------------------------
img = cv.imread('C:/cv_workspace/data/girl_laughing.jpg')
if img is None:
    sys.exit('파일을 찾을 수 없습니다.')
cv.rectangle(img, (830,30), (1000,200), (0,0,255), 2)  # 빨간 직사각형
cv.putText(img, 'laugh', (830,24), cv.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)  # 파란 글자
cv.imshow('Draw', img); cv.waitKey(); cv.destroyAllWindows()

# -------------------------------
# 6) 마우스로 사각형 찍기(왼쪽/오른쪽 버튼)
# -------------------------------
img = cv.imread('C:/cv_workspace/data/girl_laughing.jpg')
if img is None:
    sys.exit('파일을 찾을 수 없습니다.')

def draw(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONDOWN:   # 왼쪽 클릭
        cv.rectangle(img, (x,y), (x+200, y+200), (0,0,255), 2)
    elif event == cv.EVENT_RBUTTONDOWN: # 오른쪽 클릭
        cv.rectangle(img, (x,y), (x+100, y+100), (255,0,0), 2)
    cv.imshow('Drawing', img)

cv.namedWindow('Drawing'); cv.imshow('Drawing', img)
cv.setMouseCallback('Drawing', draw)
while True:
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows(); break

# -------------------------------
# 7) 드래그로 사각형 그리기
# -------------------------------
img = cv.imread('C:/cv_workspace/data/girl_laughing.jpg')
if img is None:
    sys.exit('파일을 찾을 수 없습니다.')

ix, iy = -1, -1  # 시작점 전역 변수
def draw2(event, x, y, flags, param):
    global ix, iy
    if event == cv.EVENT_LBUTTONDOWN:
        ix, iy = x, y
    elif event == cv.EVENT_LBUTTONUP:
        cv.rectangle(img, (ix, iy), (x, y), (0,0,255), 2)
    cv.imshow('Drawing', img)

cv.namedWindow('Drawing'); cv.imshow('Drawing', img)
cv.setMouseCallback('Drawing', draw2)
while True:
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows(); break

# -------------------------------
# 8) 붓처럼 칠하기(왼=파랑, 오른=빨강, 이동 중에도 칠하기)
# -------------------------------
img = cv.imread('C:/cv_workspace/data/soccer.jpg')
if img is None:
    sys.exit('파일을 찾을 수 없습니다.')
BrushSiz = 5
LColor, RColor = (255,0,0), (0,0,255)

def painting(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONDOWN:
        cv.circle(img, (x,y), BrushSiz, LColor, -1)
    elif event == cv.EVENT_RBUTTONDOWN:
        cv.circle(img, (x,y), BrushSiz, RColor, -1)
    elif event == cv.EVENT_MOUSEMOVE and flags == cv.EVENT_FLAG_LBUTTON:
        cv.circle(img, (x,y), BrushSiz, LColor, -1)
    elif event == cv.EVENT_MOUSEMOVE and flags == cv.EVENT_FLAG_RBUTTON:
        cv.circle(img, (x,y), BrushSiz, RColor, -1)
    cv.imshow('Painting', img)

cv.namedWindow('Painting'); cv.imshow('Painting', img)
cv.setMouseCallback('Painting', painting)
while True:
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows(); break

# -------------------------------
# 9) 영상 일부 자르기 + 채널 분리 보기
# -------------------------------
img = cv.imread('C:/cv_workspace/data/soccer.jpg')
if img is None:
    sys.exit('파일을 찾을 수 없습니다.')
cv.imshow('original_RGB', img)
h, w = img.shape[:2]
cv.imshow('Upper left half', img[0:h//2, 0:w//2, :])  # 왼쪽 위 절반
cv.imshow('Center half',     img[h//4:3*h//4, w//4:3*w//4, :])  # 가운데
cv.imshow('R channel', img[:,:,2])
cv.imshow('G channel', img[:,:,1])
cv.imshow('B channel', img[:,:,0])
cv.waitKey(); cv.destroyAllWindows()

# -------------------------------
# 10) R채널 히스토그램 + 오츠 이진화
# -------------------------------
img = cv.imread('C:/cv_workspace/data/soccer.jpg')
h = cv.calcHist([img], [2], None, [256], [0,256])  # R채널 히스토그램
plt.plot(h, linewidth=1); plt.title('R-channel hist'); plt.show()

t, bin_img = cv.threshold(img[:,:,2], 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)
print('오츠가 찾은 임곗값=', t)  # 예상: 대략 50~200 사이
cv.imshow('R channel', img[:,:,2])
cv.imshow('R channel binarization', bin_img)
cv.waitKey(); cv.destroyAllWindows()

# -------------------------------
# 11) 감마 보정(밝기/대비 조절 느낌)
# -------------------------------
img = cv.imread('C:/cv_workspace/data/soccer.jpg')
img = cv.resize(img, dsize=(0,0), fx=0.25, fy=0.25)
def gamma(f, gamma=1.0):
    f1 = f/255.0
    return np.uint8(255*(f1**gamma))

gc = np.hstack((gamma(img,0.5), gamma(img,0.75), gamma(img,1.0), gamma(img,2.0), gamma(img,3.0)))
cv.imshow('gamma(왼쪽=밝게, 오른쪽=어둡게)', gc)
cv.waitKey(); cv.destroyAllWindows()

# -------------------------------
# 12) 히스토그램 평활화 (어두운 사진 대비 개선)
# -------------------------------
img = cv.imread('C:/cv_workspace/data/mistyroad.jpg')
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
plt.imshow(gray, cmap='gray'); plt.xticks([]); plt.yticks([]); plt.show()
h = cv.calcHist([gray], [0], None, [256], [0,256])
plt.plot(h, linewidth=1); plt.show()

equal = cv.equalizeHist(gray)
plt.imshow(equal, cmap='gray'); plt.xticks([]); plt.yticks([]); plt.show()
h = cv.calcHist([equal], [0], None, [256], [0,256])
plt.plot(h, linewidth=1); plt.show()

# -------------------------------
# 13) 블러링 + 컨볼루션(엠보싱) 주의점
# -------------------------------
img = cv.imread('C:/cv_workspace/data/soccer.jpg')
img = cv.resize(img, dsize=(0,0), fx=0.4, fy=0.4)
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
cv.putText(gray, 'soccer', (10,20), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
cv.imshow('Original', gray)

smooth = np.hstack((cv.GaussianBlur(gray,(5,5),0.0),
                    cv.GaussianBlur(gray,(9,9),0.0),
                    cv.GaussianBlur(gray,(15,15),0.0)))
cv.imshow('Smooth', smooth)

femboss = np.array([[-1.0, 0.0, 0.0],
                    [ 0.0, 0.0, 0.0],
                    [ 0.0, 0.0, 1.0]])

gray16 = np.int16(gray)
emboss      = np.uint8(np.clip(cv.filter2D(gray16, -1, femboss) + 128, 0, 255))  # 올바른 처리
emboss_bad  = np.uint8(cv.filter2D(gray16, -1, femboss) + 128)                    # 클리핑 생략(오버/언더플로 위험)
emboss_worse= cv.filter2D(gray, -1, femboss)                                      # 자료형 주의 안 함

cv.imshow('Emboss', emboss)
cv.imshow('Emboss_bad', emboss_bad)
cv.imshow('Emboss_worse', emboss_worse)
cv.waitKey(); cv.destroyAllWindows()

# -------------------------------
# 14) 형태학적 연산(팽창/침식/열림/닫힘)
# -------------------------------
# 알파 채널(투명도)이 포함된 PNG에서 서명 영역(알파) 추출 → 이진화 후 형태학 적용
img = cv.imread('C:/cv_workspace/data/JohnHancocksSignature.png', cv.IMREAD_UNCHANGED)
t, bin_img = cv.threshold(img[:,:,3], 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)
plt.imshow(bin_img, cmap='gray'); plt.xticks([]); plt.yticks([]); plt.show()

b = bin_img[bin_img.shape[0]//2:bin_img.shape[0], 0:bin_img.shape[0]//2+1]
plt.imshow(b, cmap='gray'); plt.xticks([]); plt.yticks([]); plt.show()

se = np.uint8([[0,0,1,0,0],
               [0,1,1,1,0],
               [1,1,1,1,1],
               [0,1,1,1,0],
               [0,0,1,0,0]])  # 구조요소(모양)

b_dilation = cv.dilate(b, se, iterations=1)  # 팽창: 흰 영역이 커짐
plt.imshow(b_dilation, cmap='gray'); plt.xticks([]); plt.yticks([]); plt.show()

b_erosion = cv.erode(b, se, iterations=1)    # 침식: 흰 영역이 줄어듦
plt.imshow(b_erosion, cmap='gray'); plt.xticks([]); plt.yticks([]); plt.show()

b_closing = cv.erode(cv.dilate(b, se, iterations=1), se, iterations=1)  # 닫힘: 구멍 메움
plt.imshow(b_closing, cmap='gray'); plt.xticks([]); plt.yticks([]); plt.show()

b_opening = cv.dilate(cv.erode(b, se, iterations=1), se, iterations=1)  # 열림: 잡음 제거
plt.imshow(b_opening, cmap='gray'); plt.xticks([]); plt.yticks([]); plt.show()

# 끝!
