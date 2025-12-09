"""
11주차 - 인공신경망 (MLP)
=========================

이 코드는 가장 기본적인 인공신경망(다층 퍼셉트론, MLP)을 이용해서
MNIST 숫자(0~9)를 분류하는 예제야.

언제 이런 형태를 쓰냐면…
- 이미지가 아주 간단하거나 (28x28 수준)
- CNN까지는 필요 없고, "신경망의 기본 구조"를 이해하고 싶을 때
- 표 형태 데이터(벡터 형태)를 분류/회귀하고 싶을 때

여기서는:
1) 데이터 로드 & 전처리
2) MLP 모델 구성
3) 훈련 & 평가
4) 임의의 숫자 이미지 파일을 예측
까지 한 방에 보여줘.
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense
import tensorflow.keras.datasets as ds
from tensorflow.keras.optimizers import Adam
import cv2
import matplotlib.pyplot as plt


# ---------------------------------------------------
# 1. 데이터 로드 & 전처리
# ---------------------------------------------------
# MNIST: 28x28 흑백 손글씨 숫자 (0~9)
(x_train, y_train), (x_test, y_test) = ds.mnist.load_data()

# 28x28 → 784차원 벡터로 펼치기 (MLP는 1차원 벡터를 입력으로 받음)
x_train = x_train.reshape(60000, 784).astype(np.float32) / 255.0
x_test = x_test.reshape(10000, 784).astype(np.float32) / 255.0

# 레이블을 원-핫 인코딩으로 변환 (예: 숫자 "3" → [0,0,0,1,0,0,0,0,0,0])
y_train = tf.keras.utils.to_categorical(y_train, 10)
y_test = tf.keras.utils.to_categorical(y_test, 10)


# ---------------------------------------------------
# 2. MLP 모델 구성
# ---------------------------------------------------
# 구조:
#  입력(784) → 은닉층(512, tanh) → 출력층(10, softmax)

mlp = Sequential()
# 은닉층: 뉴런 512개, tanh 활성함수
mlp.add(Dense(units=512, activation='tanh', input_shape=(784,)))
# 출력층: 클래스 10개, 확률 출력 → softmax
mlp.add(Dense(units=10, activation='softmax'))

# 손실 함수: MSE 대신 보통은 cross-entropy를 많이 쓰지만,
# 수업에서는 개념을 위해 MSE를 사용한 예시도 자주 나옴.
mlp.compile(
    loss='MSE',
    optimizer=Adam(learning_rate=0.001),  # Adam: 실무에서 자주 쓰는 옵티마이저
    metrics=['accuracy']
)

mlp.summary()  # 레이어 구조 확인


# ---------------------------------------------------
# 3. 훈련 & 평가
# ---------------------------------------------------
hist = mlp.fit(
    x_train, y_train,
    batch_size=128,       # 한 번에 학습에 사용하는 샘플 수
    epochs=20,            # 전체 데이터를 몇 번 반복 학습할지
    validation_data=(x_test, y_test),
    verbose=2             # 로그 출력 형태 (2 = 에폭별 요약)
)

test_loss, test_acc = mlp.evaluate(x_test, y_test, verbose=0)
print(f"[MLP + Adam] 테스트 정확도: {test_acc * 100:.2f}%")

# 학습/검증 정확도 그래프 (신경망이 잘 학습됐는지 확인할 때 항상 보는 것!)
plt.plot(hist.history['accuracy'], label='train_acc')
plt.plot(hist.history['val_accuracy'], label='val_acc')
plt.xlabel('epoch')
plt.ylabel('accuracy')
plt.legend()
plt.grid()
plt.show()


# ---------------------------------------------------
# 4. 임의의 숫자 이미지 예측
# ---------------------------------------------------
# ※ 사용 상황:
#   - 손으로 쓴 숫자 이미지 파일이 있을 때,
#     그게 몇 인지 자동으로 예측하고 싶을 때.

# 주인님이 따로 준비한 0~9 손글씨 이미지 (배경 흰색, 글자 검은색)
img = cv2.imread('C:/cv_workspace/data/number.png',
                 cv2.IMREAD_GRAYSCALE)

# 네트워크 입력 크기(28x28)로 리사이즈
img = cv2.resize(img, (28, 28))
img_norm = img / 255.0  # 0~1 정규화
x_input = img_norm.reshape(1, 784)  # (1, 784) 형태로 변경

pred = mlp.predict(x_input)
predicted_label = int(np.argmax(pred))

print("모델이 예측한 숫자:", predicted_label)

# 시각적으로도 확인
plt.imshow(img, cmap='gray')
plt.title(f'Predicted: {predicted_label}')
plt.axis('off')
plt.show()
