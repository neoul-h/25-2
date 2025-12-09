############################################################
# 9주차 - 영상 처리 II (감마 보정 / 블러 & 엠보싱 / 보간법 비교)
############################################################
import cv2 as cv
import numpy as np

# ---------------------------------------------------------
# [1] 감마 보정 (Gamma Correction)
#   - 언제 쓰나?
#       * 사진이 너무 어둡거나, 밝은 영역/어두운 영역 대비를 조절하고 싶을 때
#       * 모니터 감마 보정, 사진 후보정 등
#   - 어떻게 쓰나?
#       * 이미지 픽셀값을 [0,1]로 정규화한 뒤, f(x) = x^gamma 를 적용
#       * gamma < 1 : 전체적으로 밝아짐
#       * gamma > 1 : 전체적으로 어두워짐
# ---------------------------------------------------------

# 주인님 PC에 맞게 경로 수정 필요
img = cv.imread('C:/cv_workspace/data/soccer.jpg')
# 보기 좋게 1/4 크기로 축소
img = cv.resize(img, dsize=(0, 0), fx=0.25, fy=0.25)

def gamma_correction(f, gamma=1.0):
    """
    f      : 입력 영상 (0~255 범위의 uint8)
    gamma  : 감마 계수 (0.5, 0.75, 1.0, 2.0, 3.0 등)
    return : 감마 보정된 영상 (uint8)

    사용 예시:
        bright = gamma_correction(img, 0.5)  # 밝게
        dark   = gamma_correction(img, 2.0)  # 어둡게
    """
    # 0~255 → 0~1 정규화 (실수 연산을 위함)
    f1 = f / 255.0
    # 감마 함수 적용 후 다시 0~255로 변환
    return np.uint8(255 * (f1 ** gamma))

# 여러 gamma 값을 한 번에 비교하기 위해 가로로 붙임
gamma_concat = np.hstack([
    gamma_correction(img, 0.5),   # 많이 밝게
    gamma_correction(img, 0.75),  # 약간 밝게
    gamma_correction(img, 1.0),   # 원본 수준
    gamma_correction(img, 2.0),   # 약간 어둡게
    gamma_correction(img, 3.0)    # 많이 어둡게
])

cv.imshow('9week - Gamma correction (0.5, 0.75, 1.0, 2.0, 3.0)', gamma_concat)
cv.waitKey()
cv.destroyAllWindows()


# ---------------------------------------------------------
# [2] 가우시안 블러 + 엠보싱 필터
#   - 블러(Blur):
#       * 노이즈 제거, 배경 흐리게 만들기, 전처리 용도
#   - 엠보싱(Emboss):
#       * 양각/음각처럼 입체감 있는 회색 이미지 효과
#       * 예술 필터, 텍스처 생성 등에 사용
# ---------------------------------------------------------

img = cv.imread('C:/cv_workspace/data/soccer.jpg')
img = cv.resize(img, dsize=(0, 0), fx=0.4, fy=0.4)
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

# 영상 위에 텍스트를 그려 넣는 예시 (디스플레이용)
cv.putText(gray, 'soccer', (10, 20),
           cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

cv.imshow('9week - Original gray', gray)

# 서로 다른 커널 크기의 가우시안 블러 적용
#   - kernel 크기가 커질수록 더 흐려짐
blur_stack = np.hstack([
    cv.GaussianBlur(gray, (5, 5), 0.0),   # 약간 흐림
    cv.GaussianBlur(gray, (9, 9), 0.0),   # 중간
    cv.GaussianBlur(gray, (15, 15), 0.0)  # 많이 흐림
])
cv.imshow('9week - Gaussian Smooth (5, 9, 15)', blur_stack)

# 엠보싱 커널 (왼쪽 위와 오른쪽 아래 차이를 강조)
emboss_kernel = np.array([
    [-1.0, 0.0, 0.0],
    [ 0.0, 0.0, 0.0],
    [ 0.0, 0.0, 1.0]
])

# filter2D 연산에서 오버플로우/언더플로우 방지를 위해 int16으로 변환
gray16 = np.int16(gray)

# 필터 적용 후 128을 더해서 회색(128)을 기준으로 양/음각 표현
emboss_float = cv.filter2D(gray16, -1, emboss_kernel) + 128

# 0~255 범위 밖 값 잘라주고 uint8로 캐스팅 (올바른 처리)
emboss = np.uint8(np.clip(emboss_float, 0, 255))

# 잘못된 예시(오버플로우 발생 가능)도 비교용으로 보여줌
emboss_bad = np.uint8(cv.filter2D(gray16, -1, emboss_kernel) + 128)
emboss_worse = cv.filter2D(gray, -1, emboss_kernel)  # 타입캐스팅 없이 바로 적용

cv.imshow('9week - Emboss (correct)', emboss)
cv.imshow('9week - Emboss_bad (overflow 가능)', emboss_bad)
cv.imshow('9week - Emboss_worse (직접 uint8에 필터)', emboss_worse)

cv.waitKey()
cv.destroyAllWindows()


# ---------------------------------------------------------
# [3] 보간법(Interpolation)에 따른 확대 차이
#   - 언제 쓰나?
#       * 이미지 확대/축소가 필요할 때 (UI, 썸네일, 프린트 등)
#   - 어떻게 쓰나?
#       * INTER_NEAREST  : 최근접 이웃, 계단 느낌. 픽셀 아트 확대에 사용.
#       * INTER_LINEAR   : 기본 확대, 일반적인 사진에 사용.
#       * INTER_CUBIC    : 더 부드럽지만 계산량이 많음.
# ---------------------------------------------------------

img = cv.imread('C:/cv_workspace/data/rose.png')

# 관심 영역(ROI)을 잘라서 확대만 비교
patch = img[250:350, 170:270, :]

# ROI 위치를 빨간 사각형으로 표시
img_rect = cv.rectangle(img.copy(), (170, 250), (270, 350), (255, 0, 0), 3)

# 서로 다른 보간법으로 5배 확대
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
# 10주차 - 엣지와 영역 검출 (Sobel, Canny, Contour, Hough, SLIC, N-cut, 말 외곽선)
############################################################
import cv2 as cv
import numpy as np
import skimage
from skimage import graph, segmentation
import time

# ---------------------------------------------------------
# [1] Sobel 에지 검출
#   - 언제 쓰나?
#       * 영상에서 경계(밝기 변화가 큰 자리)를 찾을 때
#   - 어떻게 쓰나?
#       * 미분(기울기)을 이용해 x방향, y방향 변화량을 계산
# ---------------------------------------------------------

img = cv.imread('C:/cv_workspace/data/soccer.jpg')
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

# x방향, y방향 기울기
grad_x = cv.Sobel(gray, cv.CV_32F, 1, 0, ksize=3)
grad_y = cv.Sobel(gray, cv.CV_32F, 0, 1, ksize=3)

# 절대값 취해서 8비트 영상으로 변환
sobel_x = cv.convertScaleAbs(grad_x)
sobel_y = cv.convertScaleAbs(grad_y)

# x, y 방향 에지를 합쳐 최종 에지 강도 계산
edge_strength = cv.addWeighted(sobel_x, 0.5, sobel_y, 0.5, 0)

cv.imshow('10week - Gray', gray)
cv.imshow('10week - Sobel X', sobel_x)
cv.imshow('10week - Sobel Y', sobel_y)
cv.imshow('10week - Sobel Edge Strength', edge_strength)
cv.waitKey()
cv.destroyAllWindows()


# ---------------------------------------------------------
# [2] Canny 에지 검출
#   - 언제 쓰나?
#       * 다음 단계에서 Contour, Hough 등으로 객체 윤곽을 따기 전에
#       * 일반적인 실무에서 가장 많이 쓰이는 에지 검출기
#   - 파라미터:
#       * threshold1 (low), threshold2 (high)
#       * 값이 낮으면 더 많은 에지가 나오고, 높으면 깔끔하지만 일부가 사라짐
# ---------------------------------------------------------

img = cv.imread('C:/cv_workspace/data/soccer.jpg')
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

canny1 = cv.Canny(gray, 50, 150)
canny2 = cv.Canny(gray, 100, 200)

cv.imshow('10week - Gray', gray)
cv.imshow('10week - Canny (50,150)', canny1)
cv.imshow('10week - Canny (100,200)', canny2)
cv.waitKey()
cv.destroyAllWindows()


# ---------------------------------------------------------
# [3] Contour(외곽선) 검출 + 길이 필터링
#   - 언제 쓰나?
#       * 이진/에지 영상에서 물체의 윤곽선을 벡터(점 집합) 형태로 얻고 싶을 때
#       * 면적, 둘레, 둥근 정도 등 기하적 특징 계산에 사용
# ---------------------------------------------------------

img = cv.imread('C:/cv_workspace/data/soccer.jpg')
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
canny = cv.Canny(gray, 100, 200)

# contour: 각 외곽선을 구성하는 점들의 리스트
contours, hierarchy = cv.findContours(
    canny, cv.RETR_LIST, cv.CHAIN_APPROX_NONE
)

# 너무 짧은 외곽선은 노이즈일 수 있으므로 길이 기준으로 필터링
long_contours = []
for c in contours:
    if c.shape[0] > 100:  # 점 개수가 100개보다 긴 것만 사용
        long_contours.append(c)

img_contour = img.copy()
cv.drawContours(img_contour, long_contours, -1, (0, 255, 0), 3)

cv.imshow('10week - Canny', canny)
cv.imshow('10week - Selected Contours (len>100)', img_contour)
cv.waitKey()
cv.destroyAllWindows()


# ---------------------------------------------------------
# [4] Hough Circle 변환으로 원 검출
#   - 언제 쓰나?
#       * 동전 개수 세기, 눈동자 위치, 공/사과 등 원형 물체 찾기
# ---------------------------------------------------------

img = cv.imread('C:/cv_workspace/data/apples.jpg')
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

# Hough 원 검출
circles = cv.HoughCircles(
    gray,
    cv.HOUGH_GRADIENT,
    dp=1,          # 해상도 스케일 (1이면 입력과 동일)
    minDist=200,   # 원 중심 사이 최소 거리
    param1=150,    # 내부적으로 쓰이는 Canny high threshold
    param2=20,     # 원으로 인정할 최소 누적값(크면 덜 검출)
    minRadius=50,
    maxRadius=120
)

img_circle = img.copy()
if circles is not None:
    for c in circles[0]:
        center = (int(c[0]), int(c[1]))
        radius = int(c[2])
        cv.circle(img_circle, center, radius, (255, 0, 0), 2)

cv.imshow('10week - Detected circles', img_circle)
cv.waitKey()
cv.destroyAllWindows()


# ---------------------------------------------------------
# [5] SLIC Superpixel 분할
#   - 언제 쓰나?
#       * 픽셀 단위가 아니라 "조각(슈퍼픽셀)" 단위로 처리하고 싶을 때
#       * 세그멘테이션, 객체 인식의 전처리
# ---------------------------------------------------------

coffee = skimage.data.coffee()  # 예제 컬러 이미지 (RGB)
cv.imshow('10week - Coffee image', cv.cvtColor(coffee, cv.COLOR_RGB2BGR))

# compactness:
#   * 색 vs 위치의 비율
#   * 값이 커질수록 공간적 위치가 더 중요해짐 (더 균일한 모양의 조각)
slic1 = segmentation.slic(coffee, compactness=20, n_segments=600)
slic2 = segmentation.slic(coffee, compactness=40, n_segments=600)

sp_img1 = segmentation.mark_boundaries(coffee, slic1)
sp_img2 = segmentation.mark_boundaries(coffee, slic2)

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
#   - 언제 쓰나?
#       * 색/위치 유사성을 모두 고려해 "비슷한 영역"을 자동으로 나누고 싶을 때
#   - 주의:
#       * 계산량이 많아서, 보통 이미지가 아주 크지 않을 때 사용
# ---------------------------------------------------------

coffee = skimage.data.coffee()

start = time.time()

# 1단계: SLIC으로 슈퍼픽셀 분할
slic = segmentation.slic(coffee, compactness=30, n_segments=600)

# 2단계: 슈퍼픽셀을 정점으로 갖는 그래프 생성 (색 평균 유사도 기반)
g = graph.rag_mean_color(coffee, slic, mode='similarity')

# 3단계: Normalized Cut으로 그래프 분할
ncut = graph.cut_normalized(slic, g)

print(coffee.shape, '영상을 분할하는데',
      time.time() - start, '초 소요')

marking = segmentation.mark_boundaries(coffee, ncut)
ncut_coffee = np.uint8(marking * 255.0)

cv.imshow('10week - Normalized cut', cv.cvtColor(ncut_coffee, cv.COLOR_RGB2BGR))
cv.waitKey()
cv.destroyAllWindows()


# ---------------------------------------------------------
# [7] 말(horse) 바이너리 영상에서 Contour + Convex Hull
#   - 언제 쓰나?
#       * 물체의 외곽선 특징(면적, 둘레, 둥근 정도) 계산
#       * 볼록 헐(Convex Hull)로 물체 모양 요약
# ---------------------------------------------------------

orig = skimage.data.horse()          # 흑백 이진 이미지 (1: 말, 0: 배경)
# 말 영역을 검은색(0) 객체로 만들기 위해 반전
img_horse = 255 - np.uint8(orig) * 255
cv.imshow('10week - Horse binary', img_horse)

# 외곽선 검출 (가장 바깥쪽 외곽선)
contours, hierarchy = cv.findContours(
    img_horse, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE
)

# 외곽선을 색깔로 표시하기 위해 BGR 컬러 이미지로 변환
horse_contour_img = cv.cvtColor(img_horse, cv.COLOR_GRAY2BGR)
cv.drawContours(horse_contour_img, contours, -1, (255, 0, 255), 2)
cv.imshow('10week - Horse with contour', horse_contour_img)

# 첫 번째(유일한) 컨투어 사용
contour = contours[0]

# 모멘트(면적, 중심, 둘레 등 계산)
m = cv.moments(contour)
area = cv.contourArea(contour)
cx, cy = m['m10'] / m['m00'], m['m01'] / m['m00']
perimeter = cv.arcLength(contour, True)
roundness = (4.0 * np.pi * area) / (perimeter * perimeter)

print('Horse area =', area)
print('center = (', cx, ',', cy, ')')
print('perimeter =', perimeter)
print('roundness =', roundness)

# 직선 근사 및 볼록 헐 표시
horse_shape_img = cv.cvtColor(img_horse, cv.COLOR_GRAY2BGR)

# 외곽선의 직선 근사 (epsilon=8 픽셀 오차 허용)
contour_approx = cv.approxPolyDP(contour, 8, True)
cv.drawContours(horse_shape_img, [contour_approx], -1, (0, 255, 0), 2)

# 볼록 헐(Convex Hull) 계산
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
# [1] 기본 MLP로 MNIST 숫자 분류
#   - 언제 쓰나?
#       * 입력이 단순 벡터(표 데이터, 작은 이미지)일 때
#       * 신경망(딥러닝)의 기본 개념 연습용
# ---------------------------------------------------------

# MNIST 데이터 로드 (28x28 손글씨 숫자)
(x_train, y_train), (x_test, y_test) = ds.mnist.load_data()

# 28x28 → 784차원 벡터로 펼치기
x_train = x_train.reshape(60000, 784).astype(np.float32) / 255.0
x_test = x_test.reshape(10000, 784).astype(np.float32) / 255.0

# 원-핫 인코딩 (0~9 → 10차원 벡터)
y_train_oh = tf.keras.utils.to_categorical(y_train, 10)
y_test_oh = tf.keras.utils.to_categorical(y_test, 10)

mlp = Sequential()
# 은닉층: 뉴런 512개, 'tanh' 활성함수
mlp.add(Dense(units=512, activation='tanh', input_shape=(784,)))
# 출력층: 10개 클래스, 'softmax' 확률 분포 출력
mlp.add(Dense(units=10, activation='softmax'))

# 손실함수: MSE, 옵티마이저: SGD (경사하강법)
mlp.compile(
    loss='MSE',
    optimizer=SGD(learning_rate=0.01),
    metrics=['accuracy']
)

hist_mlp = mlp.fit(
    x_train, y_train_oh,
    batch_size=128,
    epochs=50,
    validation_data=(x_test, y_test_oh),
    verbose=2
)

test_loss, test_acc = mlp.evaluate(x_test, y_test_oh, verbose=0)
print('[11주차 기본 MLP+SGD] 테스트 정확도 =', test_acc * 100)


# ---------------------------------------------------------
# [2] 학습된 MLP로 주인님 숫자 이미지 예측
#   - 언제 쓰나?
#       * 직접 그린 숫자 이미지가 몇인지 모델에게 물어볼 때
#   - 사용 방법:
#       * 28x28 흑백 이미지, 숫자 부분이 밝고 배경이 어두운 형태 권장
# ---------------------------------------------------------

img = cv2.imread('C:/cv_workspace/data/number.png', cv2.IMREAD_GRAYSCALE)
img = cv2.resize(img, (28, 28))   # 네트워크 입력 크기에 맞춤
img_norm = img / 255.0           # 0~1 정규화
x_input = img_norm.reshape(1, 784)

pred = mlp.predict(x_input)
predicted_label = int(np.argmax(pred))
print('[11주차 기본 MLP] 예측된 숫자:', predicted_label)


# ---------------------------------------------------------
# [3] SGD vs Adam 옵티마이저 비교
#   - 언제 쓰나?
#       * 어떤 옵티마이저가 학습을 더 잘하는지 실험할 때
#       * SGD는 단순하지만 느릴 수 있고, Adam은 보통 더 빠르게 수렴
# ---------------------------------------------------------

# 다시 데이터 준비 (독립적인 실험으로 보고 재정의)
(x_train, y_train), (x_test, y_test) = ds.mnist.load_data()
x_train = x_train.reshape(60000, 784).astype(np.float32) / 255.0
x_test = x_test.reshape(10000, 784).astype(np.float32) / 255.0
y_train_oh = tf.keras.utils.to_categorical(y_train, 10)
y_test_oh = tf.keras.utils.to_categorical(y_test, 10)

# (1) SGD
mlp_sgd = Sequential()
mlp_sgd.add(Dense(512, activation='tanh', input_shape=(784,)))
mlp_sgd.add(Dense(10, activation='softmax'))

mlp_sgd.compile(loss='MSE', optimizer=SGD(learning_rate=0.01),
                metrics=['accuracy'])
hist_sgd = mlp_sgd.fit(
    x_train, y_train_oh,
    batch_size=128,
    epochs=50,
    validation_data=(x_test, y_test_oh),
    verbose=2
)
print('[11주차] SGD 정확률 =',
      mlp_sgd.evaluate(x_test, y_test_oh, verbose=0)[1] * 100)

# (2) Adam
mlp_adam = Sequential()
mlp_adam.add(Dense(512, activation='tanh', input_shape=(784,)))
mlp_adam.add(Dense(10, activation='softmax'))

mlp_adam.compile(loss='MSE', optimizer=Adam(learning_rate=0.001),
                 metrics=['accuracy'])
hist_adam = mlp_adam.fit(
    x_train, y_train_oh,
    batch_size=128,
    epochs=50,
    validation_data=(x_test, y_test_oh),
    verbose=2
)
print('[11주차] Adam 정확률 =',
      mlp_adam.evaluate(x_test, y_test_oh, verbose=0)[1] * 100)

# 학습 곡선 비교 그래프 (SGD vs Adam)
plt.figure()
plt.plot(hist_sgd.history['accuracy'], 'r--')
plt.plot(hist_sgd.history['val_accuracy'], 'r')
plt.plot(hist_adam.history['accuracy'], 'b--')
plt.plot(hist_adam.history['val_accuracy'], 'b')
plt.title('11주차 - SGD vs Adam accuracy')
plt.ylim((0.7, 1.0))
plt.xlabel('epochs')
plt.ylabel('accuracy')
plt.legend(['train_sgd', 'val_sgd', 'train_adam', 'val_adam'])
plt.grid()
plt.show()


# ---------------------------------------------------------
# [4] 더 깊은 MLP(dmlp) 구성 및 성능 확인
#   - 언제 쓰나?
#       * 더 복잡한 모델이 필요하거나, 표현력이 부족할 때
#       * 층/뉴런 수를 늘리면 표현력 ↑, 과적합 위험도 ↑
# ---------------------------------------------------------

(x_train, y_train), (x_test, y_test) = ds.mnist.load_data()
x_train = x_train.reshape(60000, 784).astype(np.float32) / 255.0
x_test = x_test.reshape(10000, 784).astype(np.float32) / 255.0
y_train_oh = tf.keras.utils.to_categorical(y_train, 10)
y_test_oh = tf.keras.utils.to_categorical(y_test, 10)

dmlp = Sequential()
dmlp.add(Dense(1024, activation='relu', input_shape=(784,)))
dmlp.add(Dense(512, activation='relu'))
dmlp.add(Dense(512, activation='relu'))
dmlp.add(Dense(10, activation='softmax'))

dmlp.compile(
    loss='categorical_crossentropy',
    optimizer=Adam(learning_rate=0.0001),
    metrics=['accuracy']
)

hist_deep = dmlp.fit(
    x_train, y_train_oh,
    batch_size=128,
    epochs=50,
    validation_data=(x_test, y_test_oh),
    verbose=2
)

print('[11주차 깊은 MLP] 정확률 =',
      dmlp.evaluate(x_test, y_test_oh, verbose=0)[1] * 100)

# 학습된 모델 저장 (나중에 불러와 재사용 용도)
dmlp.save('dmlp_trained.h5')

# 정확도/손실 그래프
plt.figure()
plt.plot(hist_deep.history['accuracy'])
plt.plot(hist_deep.history['val_accuracy'])
plt.title('11주차 Deep MLP - Accuracy')
plt.xlabel('epochs')
plt.ylabel('accuracy')
plt.legend(['train', 'val'])
plt.grid()
plt.show()

plt.figure()
plt.plot(hist_deep.history['loss'])
plt.plot(hist_deep.history['val_loss'])
plt.title('11주차 Deep MLP - Loss')
plt.xlabel('epochs')
plt.ylabel('loss')
plt.legend(['train', 'val'])
plt.grid()
plt.show()

# 깊은 MLP로 숫자 이미지 예측
img = cv2.imread('C:/cv_workspace/data/number.png', cv2.IMREAD_GRAYSCALE)
img = cv2.resize(img, (28, 28))
img_norm = img / 255.0
x_input = img_norm.reshape(1, 784)
pred = dmlp.predict(x_input)
predicted_label = int(np.argmax(pred))
print('[11주차 깊은 MLP] 예측된 숫자:', predicted_label)

############################################################
# 12주차 - 합성곱 신경망 I (CNN 기초, Fashion-MNIST, 필터 시각화)
############################################################
import keras
from sklearn.model_selection import train_test_split

# ---------------------------------------------------------
# [간단 Conv2D / MaxPooling 예시 레이어]
#   - 언제 쓰나?
#       * 이미지 입력(높이, 너비, 채널)을 처리할 때
#       * 국소 영역(3x3 등)에 대한 합성곱 필터 적용
# ---------------------------------------------------------

keras.layers.Conv2D(10, kernel_size=(3, 3), activation='relu')
keras.layers.Conv2D(10, kernel_size=(3, 3), activation='relu', padding='same')
keras.layers.Conv2D(10, kernel_size=(3, 3), activation='relu',
                    padding='same', strides=1)
keras.layers.MaxPooling2D(2)
keras.layers.MaxPooling2D(2, strides=2, padding='valid')

# ---------------------------------------------------------
# [1] Fashion-MNIST 데이터로 CNN 학습
# ---------------------------------------------------------

(train_input, train_target), (test_input, test_target) = \
    keras.datasets.fashion_mnist.load_data()

# (N, 28, 28) → (N, 28, 28, 1) : 채널 차원 추가 + 정규화
train_scaled = train_input.reshape(-1, 28, 28, 1) / 255.0
test_scaled = test_input.reshape(-1, 28, 28, 1) / 255.0

# train / validation 분리
train_scaled, val_scaled, train_target, val_target = train_test_split(
    train_scaled, train_target, test_size=0.2, random_state=42
)

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

model.summary()

# 모델 컴파일
model.compile(
    optimizer='adam',                        # 대부분 CNN에서 기본으로 쓰는 옵티마이저
    loss='sparse_categorical_crossentropy',  # 라벨이 정수(0~9)일 때
    metrics=['accuracy']
)

# 가장 좋은 모델만 저장하기 위한 콜백
checkpoint_cb = keras.callbacks.ModelCheckpoint(
    'best-cnn-model.keras', save_best_only=True
)

# 조기 종료 콜백
early_stopping_cb = keras.callbacks.EarlyStopping(
    patience=2, restore_best_weights=True
)

# 학습
history = model.fit(
    train_scaled, train_target,
    epochs=20,
    validation_data=(val_scaled, val_target),
    callbacks=[checkpoint_cb, early_stopping_cb],
    verbose=2
)

# 학습/검증 손실 곡선
plt.figure()
plt.plot(history.history['loss'], label='train_loss')
plt.plot(history.history['val_loss'], label='val_loss')
plt.xlabel('epoch')
plt.ylabel('loss')
plt.legend()
plt.grid()
plt.show()

# 검증/테스트 정확도
val_loss, val_acc = model.evaluate(val_scaled, val_target, verbose=0)
print('[12주차 CNN] 검증 정확도:', val_acc)
test_loss, test_acc = model.evaluate(test_scaled, test_target, verbose=0)
print('[12주차 CNN] 테스트 정확도:', test_acc)

# 임의 샘플 예측
preds = model.predict(val_scaled[0:1])
print('[12주차 CNN] 예측 확률 벡터:', preds)

plt.figure()
plt.bar(range(10), preds[0])
plt.xlabel('class index(0~9)')
plt.ylabel('prob.')
plt.show()

classes = ['티셔츠', '바지', '스웨터', '드레스', '코트',
           '샌달', '셔츠', '스니커즈', '가방', '앵클 부츠']
print('[12주차 CNN] 예측 클래스 이름:', classes[int(np.argmax(preds))])

# 테스트셋 평가
ev = model.evaluate(test_scaled, test_target, verbose=0)
print('[12주차 CNN] Test loss:', ev[0])
print('[12주차 CNN] Test accuracy:', ev[1])

# ---------------------------------------------------------
# [2] 첫 합성곱층의 필터 가중치 시각화
#   - 언제 쓰나?
#       * CNN이 어떤 패턴(가장자리, 점, 텍스처 등)을 학습했는지 보고 싶을 때
# ---------------------------------------------------------

conv = model.layers[1]  # 첫 Conv2D 레이어
print('Conv weights shape:', conv.weights[0].shape,
      'bias shape:', conv.weights[1].shape)

conv_weights = conv.weights[0].numpy()
print('Conv mean/std:', conv_weights.mean(), conv_weights.std())

plt.figure()
plt.hist(conv_weights.reshape(-1, 1))
plt.xlabel('weight')
plt.ylabel('count')
plt.show()

# 32개 필터 중 앞 32개(2x16 배치) 시각화
fig, axs = plt.subplots(2, 16, figsize=(15, 2))
for i in range(2):
    for j in range(16):
        axs[i, j].imshow(conv_weights[:, :, 0, i * 16 + j],
                         vmin=-0.5, vmax=0.5, cmap='gray')
        axs[i, j].axis('off')
plt.show()


# ---------------------------------------------------------
# [3] 랜덤 초기화된 Conv 필터와 비교
# ---------------------------------------------------------

no_training_model = keras.Sequential()
no_training_model.add(keras.layers.Input(shape=(28, 28, 1)))
no_training_model.add(keras.layers.Conv2D(
    32, kernel_size=3, activation='relu', padding='same'))

no_training_conv = no_training_model.layers[1]
no_training_weights = no_training_conv.weights[0].numpy()
print('No-training conv mean/std:',
      no_training_weights.mean(), no_training_weights.std())

plt.figure()
plt.hist(no_training_weights.reshape(-1, 1))
plt.xlabel('weight')
plt.ylabel('count')
plt.show()

fig, axs = plt.subplots(2, 16, figsize=(15, 2))
for i in range(2):
    for j in range(16):
        axs[i, j].imshow(no_training_weights[:, :, 0, i * 16 + j],
                         vmin=-0.5, vmax=0.5, cmap='gray')
        axs[i, j].axis('off')
plt.show()


# ---------------------------------------------------------
# [4] Feature map(중간 활성값) 시각화
#   - 언제 쓰나?
#       * 특정 입력 이미지에 대해 Conv 층이 어떤 특징을 추출했는지 확인할 때
# ---------------------------------------------------------

# 모델의 입력과 첫 Conv레이어 출력을 연결하는 새 모델
conv_acti = keras.Model(model.inputs, model.layers[1].output)

(train_input2, train_target2), _ = keras.datasets.fashion_mnist.load_data()
plt.imshow(train_input2[0], cmap='gray_r')
plt.title('Sample input image')
plt.show()

ankle_boot = train_input2[0:1].reshape(-1, 28, 28, 1) / 255.0
feature_maps = conv_acti.predict(ankle_boot)
print('1st Conv feature map shape:', feature_maps.shape)

fig, axs = plt.subplots(4, 8, figsize=(15, 8))
for i in range(4):
    for j in range(8):
        axs[i, j].imshow(feature_maps[0, :, :, i * 8 + j], cmap='gray')
        axs[i, j].axis('off')
plt.show()

# 두 번째 Conv 층도 동일하게 시각화
conv2_acti = keras.Model(model.inputs, model.layers[3].output)
feature_maps2 = conv2_acti.predict(ankle_boot)
print('2nd Conv feature map shape:', feature_maps2.shape)

fig, axs = plt.subplots(8, 8, figsize=(12, 12))
for i in range(8):
    for j in range(8):
        axs[i, j].imshow(feature_maps2[0, :, :, i * 8 + j], cmap='gray')
        axs[i, j].axis('off')
plt.show()

############################################################
# 13주차 - 합성곱 신경망 II (LeNet-5, 데이터 증강, ResNet50)
############################################################
import tensorflow.keras.datasets as ds
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dropout, Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# ---------------------------------------------------------
# [1] LeNet-5 스타일 CNN (MNIST)
#   - 고전 구조 연습용, 작은 이미지(28x28)에 적합
# ---------------------------------------------------------

(x_train, y_train), (x_test, y_test) = ds.mnist.load_data()
x_train = x_train.reshape(60000, 28, 28, 1).astype(np.float32) / 255.0
x_test = x_test.reshape(10000, 28, 28, 1).astype(np.float32) / 255.0

y_train_oh = tf.keras.utils.to_categorical(y_train, 10)
y_test_oh = tf.keras.utils.to_categorical(y_test, 10)

cnn = Sequential()
cnn.add(Conv2D(6, (5, 5), padding='same',
               activation='relu', input_shape=(28, 28, 1)))     # C1
cnn.add(MaxPooling2D(pool_size=(2, 2), strides=2))             # S2
cnn.add(Conv2D(16, (5, 5), padding='valid', activation='relu'))# C3
cnn.add(MaxPooling2D(pool_size=(2, 2), strides=2))             # S4
cnn.add(Conv2D(120, (5, 5), padding='valid', activation='relu'))# C5
cnn.add(Flatten())
cnn.add(Dense(units=84, activation='relu'))                    # F6
cnn.add(Dense(units=10, activation='softmax'))

cnn.compile(
    loss='categorical_crossentropy',
    optimizer=Adam(learning_rate=0.001),
    metrics=['accuracy']
)

cnn.summary()
hist = cnn.fit(
    x_train, y_train_oh,
    batch_size=128,
    epochs=15,
    validation_data=(x_test, y_test_oh),
    verbose=2
)
test_loss, test_acc = cnn.evaluate(x_test, y_test_oh, verbose=0)
print('[13주차 LeNet-5 CNN] 테스트 정확도:', test_acc * 100)

plt.figure()
plt.plot(hist.history['accuracy'], label='train_acc')
plt.plot(hist.history['val_accuracy'], label='val_acc')
plt.xlabel('epoch')
plt.ylabel('accuracy')
plt.legend()
plt.grid()
plt.show()


# ---------------------------------------------------------
# [2] CIFAR-10 데이터 증강(ImageDataGenerator)
#   - 데이터가 부족할 때 회전/이동/뒤집기로 가상의 데이터를 늘림
#   - 이 코드는 "어떻게 변하는지" 시각화만 함
# ---------------------------------------------------------

(x_train_c, y_train_c), _ = ds.cifar10.load_data()
x_train_c = x_train_c.astype('float32') / 255.0

# 시각화를 위해 앞 15개만 사용
x_vis = x_train_c[0:15]
y_vis = y_train_c[0:15]

class_names_cifar = ['airplane', 'automobile', 'bird', 'cat',
                     'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

plt.figure(figsize=(20, 2))
plt.suptitle('13주차 - First 15 CIFAR10 images')
for i in range(15):
    plt.subplot(1, 15, i + 1)
    plt.imshow(x_vis[i])
    plt.xticks([]); plt.yticks([])
    plt.title(class_names_cifar[int(y_vis[i])])
plt.show()

batch_size = 4

generator = ImageDataGenerator(
    rotation_range=20.0,      # 최대 20도 회전
    width_shift_range=0.2,    # 가로 이동
    height_shift_range=0.2,   # 세로 이동
    horizontal_flip=True      # 좌우 반전
)

gen = generator.flow(x_vis, y_vis, batch_size=batch_size)

for trial in range(3):
    img_batch, label_batch = next(gen)
    plt.figure(figsize=(8, 2.4))
    plt.suptitle(f'13주차 - Augmented images trial {trial + 1}')
    for i in range(batch_size):
        plt.subplot(1, batch_size, i + 1)
        plt.imshow(img_batch[i])
        plt.xticks([]); plt.yticks([])
        plt.title(class_names_cifar[int(label_batch[i])])
    plt.show()


# ---------------------------------------------------------
# [3] 사전학습된 ResNet50으로 이미지넷 분류
#   - 언제 쓰나?
#       * 일반 사진(224x224 RGB)을 1000개 클래스 중 하나로 분류
#       * 전이학습(Transfer Learning)의 기반 모델로 자주 사용
# ---------------------------------------------------------

import cv2 as cv
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input, decode_predictions

resnet_model = ResNet50(weights='imagenet')   # ImageNet으로 미리 학습된 모델

img = cv.imread('C:/cv_workspace/data/rabbit.jpg')  # 주인님 경로에 맞게 수정
x = cv.resize(img, (224, 224))
x = np.reshape(x, (1, 224, 224, 3))
x = preprocess_input(x)

preds = resnet_model.predict(x)
top5 = decode_predictions(preds, top=5)[0]
print('[13주차 ResNet50] 예측 결과 top-5:', top5)

# 이미지 위에 예측 결과 텍스트로 표시
for i in range(5):
    label_text = f"{top5[i][1]}: {top5[i][2]:.3f}"
    cv.putText(img, label_text, (10, 20 + i * 20),
               cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

cv.imshow('13주차 - ResNet50 Recognition result', img)
cv.waitKey()
cv.destroyAllWindows()


############################################################
# 14주차 - YOLO v3 객체 검출 (정지 이미지 + 카메라)
############################################################
import sys

path = 'C:/cv_workspace/data/'   # YOLO 관련 파일 및 테스트 이미지 경로

def construct_yolo_v3():
    """
    YOLO v3 네트워크와 클래스 이름을 로드하는 함수.

    - 언제 / 어떻게 쓰이나?
      * 프로그램 시작 시 한 번만 호출해서 모델과 클래스 목록을 준비해 둔다.
      * 이후 여러 이미지/영상에 같은 모델을 재사용.

    반환:
        model       : YOLO v3 DNN 네트워크
        out_layers  : 출력 레이어 이름 리스트
        class_names : coco_names.txt에 정의된 클래스 이름들
    """
    with open(path + 'coco_names.txt', 'r', encoding='utf-8') as f:
        class_names = [line.strip() for line in f.readlines()]

    model = cv.dnn.readNet(path + 'yolov3.weights',
                           path + 'yolov3.cfg')
    layer_names = model.getLayerNames()
    out_layers = [layer_names[i - 1] for i in model.getUnconnectedOutLayers()]

    return model, out_layers, class_names


def yolo_detect(img, yolo_model, out_layers,
                conf_thresh=0.5, nms_thresh=0.4):
    """
    한 장의 BGR 이미지를 입력받아 YOLO v3로 객체를 검출.

    매개변수:
        img        : 입력 BGR 이미지
        yolo_model : construct_yolo_v3()로 생성한 네트워크
        out_layers : YOLO의 출력 레이어 이름들
        conf_thresh: confidence threshold (기본 0.5)
        nms_thresh : NMS(IOU) threshold (기본 0.4)

    반환:
        objects 리스트
        각 원소 형식: [x1, y1, x2, y2, confidence, class_id]
    """
    h, w = img.shape[:2]

    # 이미지를 YOLO 입력 형식으로 blob 변환
    blob = cv.dnn.blobFromImage(
        img, 1.0 / 255, (448, 448),
        (0, 0, 0), swapRB=True
    )

    yolo_model.setInput(blob)
    outputs = yolo_model.forward(out_layers)

    boxes = []
    scores = []
    class_ids = []

    # 출력 feature map을 순회하며 confidence가 높은 박스만 모음
    for output in outputs:
        for det in output:
            # det: [tx, ty, tw, th, objectness, p1, p2, ... p80]
            class_scores = det[5:]
            class_id = int(np.argmax(class_scores))
            confidence = float(class_scores[class_id])

            if confidence > conf_thresh:
                cx = int(det[0] * w)
                cy = int(det[1] * h)
                bw = int(det[2] * w)
                bh = int(det[3] * h)

                x1 = int(cx - bw / 2)
                y1 = int(cy - bh / 2)
                x2 = x1 + bw
                y2 = y1 + bh

                boxes.append([x1, y1, x2, y2])
                scores.append(confidence)
                class_ids.append(class_id)

    # Non-Maximum Suppression으로 중복 박스 제거
    indices = cv.dnn.NMSBoxes(boxes, scores, conf_thresh, nms_thresh)

    result = []
    for i in range(len(boxes)):
        if i in indices:
            x1, y1, x2, y2 = boxes[i]
            result.append([x1, y1, x2, y2, scores[i], class_ids[i]])

    return result


def run_yolo_on_image():
    """
    정지 이미지 한 장에 대해 YOLO v3를 수행하고
    결과를 화면에 표시하는 예제 함수.

    - 실전에서는:
      * 여러 이미지 파일에 대해 반복 호출
      * 또는 동영상/웹캠 프레임에도 동일한 방식으로 처리
    """
    model, out_layers, class_names = construct_yolo_v3()
    colors = np.random.uniform(0, 255, size=(len(class_names), 3))

    img = cv.imread(path + 'soccer.jpg')
    if img is None:
        sys.exit('이미지 파일을 찾을 수 없습니다.')

    objects = yolo_detect(img, model, out_layers)

    for x1, y1, x2, y2, confidence, cid in objects:
        label = f"{class_names[cid]} {confidence:.2f}"
        color = colors[cid]
        cv.rectangle(img, (x1, y1), (x2, y2), color, 2)
        cv.putText(img, label, (x1, y1 - 10),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    cv.imshow('14주차 - YOLO v3 detection (image)', img)
    cv.waitKey()
    cv.destroyAllWindows()


# ---------------------------------------------------------
# [옵션] 카메라(웹캠) 입력에 YOLO 적용 (실습 환경에 맞게 필요 시 사용)
#   - 언제 쓰나?
#       * 실시간 객체 검출 데모할 때
# ---------------------------------------------------------

def run_yolo_on_camera():
    model, out_layers, class_names = construct_yolo_v3()
    colors = np.random.uniform(0, 255, size=(len(class_names), 3))

    cap = cv.VideoCapture(0)  # 기본 웹캠

    if not cap.isOpened():
        print('카메라를 열 수 없습니다.')
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        objects = yolo_detect(frame, model, out_layers)

        for x1, y1, x2, y2, confidence, cid in objects:
            label = f"{class_names[cid]} {confidence:.2f}"
            color = colors[cid]
            cv.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv.putText(frame, label, (x1, y1 - 10),
                       cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        cv.imshow('14주차 - YOLO v3 detection (camera)', frame)

        # q 키를 누르면 종료
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()


# 예시로 정지 이미지 YOLO만 바로 실행하고 싶으면 아래 호출
# run_yolo_on_image()
# 카메라 실습을 하고 싶으면 아래 호출
# run_yolo_on_camera()
