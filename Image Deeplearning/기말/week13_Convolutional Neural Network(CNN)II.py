"""
13주차 - 합성곱 신경망 II (LeNet-5, 데이터 증강)
================================================

언제 이런 구조를 쓰냐면…
- 작은 해상도의 이미지 (MNIST 등)를 다룰 때
- 고전 논문 구조(LeNet-5)를 이해하고 싶을 때
- 데이터가 부족해서 "데이터 증강"이 꼭 필요할 때

이 코드는:
1) MNIST에 LeNet-5 스타일 CNN 적용
2) CIFAR-10에 데이터 증강만 적용해서 이미지가 어떻게 변하는지 시각화
"""

import numpy as np
import tensorflow as tf
import tensorflow.keras.datasets as ds
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt

# ---------------------------------------------------
# 1. LeNet-5 스타일 CNN (MNIST)
# ---------------------------------------------------
(x_train, y_train), (x_test, y_test) = ds.mnist.load_data()
x_train = x_train.reshape(60000, 28, 28, 1).astype(np.float32) / 255.0
x_test = x_test.reshape(10000, 28, 28, 1).astype(np.float32) / 255.0

y_train = tf.keras.utils.to_categorical(y_train, 10)
y_test = tf.keras.utils.to_categorical(y_test, 10)

# LeNet-5 구조를 흉내 낸 CNN
cnn = Sequential()
# C1: 6개의 5x5 필터, padding='same'
cnn.add(Conv2D(6, (5, 5), padding='same',
               activation='relu', input_shape=(28, 28, 1)))
# S2: 2x2 Max Pooling
cnn.add(MaxPooling2D(pool_size=(2, 2), strides=2))
# C3: 16개의 5x5 필터
cnn.add(Conv2D(16, (5, 5), padding='valid', activation='relu'))
# S4: 2x2 Max Pooling
cnn.add(MaxPooling2D(pool_size=(2, 2), strides=2))
# C5: 120개의 5x5 필터 → 1x1x120
cnn.add(Conv2D(120, (5, 5), padding='valid', activation='relu'))
cnn.add(Flatten())
# F6: 완전연결 84
cnn.add(Dense(units=84, activation='relu'))
# Output: 10 클래스
cnn.add(Dense(units=10, activation='softmax'))

cnn.compile(
    loss='categorical_crossentropy',
    optimizer=Adam(learning_rate=0.001),
    metrics=['accuracy']
)

cnn.summary()

hist = cnn.fit(
    x_train, y_train,
    batch_size=128,
    epochs=15,
    validation_data=(x_test, y_test),
    verbose=2
)

test_loss, test_acc = cnn.evaluate(x_test, y_test, verbose=0)
print(f"[LeNet-5 CNN] 테스트 정확도: {test_acc * 100:.2f}%")

plt.plot(hist.history['accuracy'], label='train_acc')
plt.plot(hist.history['val_accuracy'], label='val_acc')
plt.xlabel('epoch')
plt.ylabel('accuracy')
plt.legend()
plt.grid()
plt.show()


# ---------------------------------------------------
# 2. CIFAR-10 데이터 증강 (ImageDataGenerator)
# ---------------------------------------------------
# ※ 사용 상황:
#   - 학습 데이터가 부족할 때
#   - 회전/이동/뒤집기 등으로 다양한 변형을 만들어
#     모델이 더 튼튼하게 일반화되도록 돕고 싶을 때

(x_train, y_train), _ = ds.cifar10.load_data()
x_train = x_train.astype('float32') / 255.0

class_names = ['airplane', 'automobile', 'bird', 'cat',
               'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

x_vis = x_train[0:8]
y_vis = y_train[0:8]

# 원본 몇 개 먼저 보기
plt.figure(figsize=(8, 2))
for i in range(8):
    plt.subplot(1, 8, i + 1)
    plt.imshow(x_vis[i])
    plt.xticks([]); plt.yticks([])
    plt.title(class_names[int(y_vis[i])])
plt.suptitle('Original images')
plt.show()

# ImageDataGenerator로 증강 설정
generator = ImageDataGenerator(
    rotation_range=20.0,      # 최대 20도 회전
    width_shift_range=0.2,    # 가로로 20%까지 평행 이동
    height_shift_range=0.2,   # 세로로 20%까지 평행 이동
    horizontal_flip=True      # 좌우 반전
)

gen = generator.flow(x_vis, y_vis, batch_size=4)

# 3번 정도만 샘플을 뽑아서 어떻게 변하는지 시각화
for trial in range(3):
    img_batch, label_batch = next(gen)

    plt.figure(figsize=(8, 2))
    plt.suptitle(f'Augmented images - trial {trial+1}')
    for i in range(4):
        plt.subplot(1, 4, i + 1)
        plt.imshow(img_batch[i])
        plt.xticks([]); plt.yticks([])
        plt.title(class_names[int(label_batch[i])])
    plt.show()
