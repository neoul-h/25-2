"""
12주차 - 합성곱 신경망 I (CNN 기초)
===================================

이 코드는 합성곱 신경망(CNN)을 이용해 Fashion-MNIST를 분류하는 예제야.

언제 CNN을 쓰냐면…
- 입력이 '이미지'이고, 공간적인 구조(가까운 픽셀끼리 관련)가 중요할 때
- MLP로 하면 파라미터 수가 너무 많을 때
- 객체 인식, 얼굴 인식, 자율주행, 의료 영상 등 이미지 관련 거의 전부!

여기서는:
1) 데이터 전처리 (28x28 → (28,28,1))
2) 간단 CNN 구성 (Conv → Pool → Conv → Pool → Dense)
3) Dropout으로 과적합 방지
4) 학습 / 평가 / 예측
까지 해본다.
"""

import keras
from sklearn.model_selection import train_test_split
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------
# 1. 데이터 로드 & 전처리
# ---------------------------------------------------
(train_input, train_target), (test_input, test_target) = \
    keras.datasets.fashion_mnist.load_data()

# CNN은 (배치, 높이, 너비, 채널수) 형태의 입력을 쓰기 때문에
# 28x28 → (28,28,1)로 채널 차원을 하나 늘려 준다.
train_scaled = train_input.reshape(-1, 28, 28, 1) / 255.0
test_scaled = test_input.reshape(-1, 28, 28, 1) / 255.0

# 훈련세트를 다시 훈련/검증으로 나눈다 (과적합 체크 위해)
train_scaled, val_scaled, train_target, val_target = train_test_split(
    train_scaled, train_target, test_size=0.2, random_state=42
)

class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
               'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

# ---------------------------------------------------
# 2. CNN 모델 구성
# ---------------------------------------------------
model = keras.Sequential()

# ★ 입력레이어: (28,28,1) 흑백 이미지
model.add(keras.layers.Input(shape=(28, 28, 1)))

# ★ 첫 번째 합성곱 + 풀링 블록
#   - 필터 32개, 3x3, padding='same' → 출력 크기 유지
model.add(keras.layers.Conv2D(
    32, kernel_size=3, activation='relu', padding='same'
))
model.add(keras.layers.MaxPooling2D(2))
# MaxPooling2D(2) == 2x2 영역에서 가장 큰 값만 남기기 (크기 반으로 줄어듦)

# ★ 두 번째 합성곱 + 풀링 블록
model.add(keras.layers.Conv2D(
    64, kernel_size=3, activation='relu', padding='same'
))
model.add(keras.layers.MaxPooling2D(2))

# ★ 완전연결층으로 넘어가기 전에 1차원으로 펼치기
model.add(keras.layers.Flatten())

# 은닉층: 뉴런 100개, relu
model.add(keras.layers.Dense(100, activation='relu'))

# Dropout(0.4) : 학습 때 임의로 뉴런 40%를 꺼서
#   → 특정 뉴런에 과도하게 의존하는 것을 막고 일반화 성능 향상
model.add(keras.layers.Dropout(0.4))

# 출력층: 10 클래스, softmax
model.add(keras.layers.Dense(10, activation='softmax'))

model.summary()


# ---------------------------------------------------
# 3. 모델 컴파일 (학습 설정)
# ---------------------------------------------------
# optimizer='adam' : 대부분의 분류 CNN에서 기본처럼 사용하는 옵티마이저
# loss='sparse_categorical_crossentropy' :
#   - 라벨이 one-hot이 아니라 정수(0~9)일 때 사용하는 다중분류 손실
model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# 가장 좋은 모델만 저장하기 위한 체크포인트 콜백
checkpoint_cb = keras.callbacks.ModelCheckpoint(
    'best-cnn-model.keras', save_best_only=True
)

# 검증 성능이 n epoch 동안 좋아지지 않으면 학습 조기 종료
early_stopping_cb = keras.callbacks.EarlyStopping(
    patience=2, restore_best_weights=True
)


# ---------------------------------------------------
# 4. 모델 학습
# ---------------------------------------------------
history = model.fit(
    train_scaled, train_target,
    epochs=20,
    validation_data=(val_scaled, val_target),
    callbacks=[checkpoint_cb, early_stopping_cb],
    verbose=2
)

# 학습 곡선 그려 보기 (항상 신경망 학습 후 체크하는 습관!)
plt.plot(history.history['loss'], label='train_loss')
plt.plot(history.history['val_loss'], label='val_loss')
plt.xlabel('epoch')
plt.ylabel('loss')
plt.legend()
plt.grid()
plt.show()


# ---------------------------------------------------
# 5. 평가 & 예측 확인
# ---------------------------------------------------
val_loss, val_acc = model.evaluate(val_scaled, val_target, verbose=0)
print(f"검증 정확도: {val_acc * 100:.2f}%")

test_loss, test_acc = model.evaluate(test_scaled, test_target, verbose=0)
print(f"테스트 정확도: {test_acc * 100:.2f}%")

# 임의 샘플 하나의 예측 결과 보기
sample = val_scaled[0:1]
pred = model.predict(sample)
pred_class = int(np.argmax(pred))

plt.imshow(val_scaled[0].reshape(28, 28), cmap='gray')
plt.title(f"예측: {class_names[pred_class]}")
plt.axis('off')
plt.show()
