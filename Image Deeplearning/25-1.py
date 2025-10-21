# 학번 : 202104008 / 이름: 김진우

import pandas as pd
import numpy as np

# 1번. 파일을 읽고 데이터의 앞부분 10행을 출력하는 코드
#dir="C:/ml_workspace/data.csv"
df = pd.read_csv("/Users/neoul_h/25-1/ml_workspace/data.csv")
print("1번. 데이터 앞 10행 출력:")
print(df.head(10))
print()

# 2번. 남자의 수와 여자의 수를 각각 구하는 코드
print("2번. 성별에 따른 인원 수:")
gender_onehot = pd.get_dummies(df["Gender"])
print(gender_onehot.sum())
print()

# 3번. 흡연자인 행의 인덱스를 출력하는 코드
print("3번. 흡연자 인덱스:")
print(np.where(pd.get_dummies(df["Smoker"])["yes"] == 1))
print()

# 4번. 흡연자 중 성별에 따라 흡연 기간의 평균을 구하는 코드
print("4번. 흡연자 성별별 흡연 기간 평균:")
smoker_idx = np.where(pd.get_dummies(df["Smoker"])["yes"] == 1)
print(df.loc[smoker_idx].groupby("Gender")["HowLong"].mean())
print()

# 5번. 각 행마다 BMI를 구하여 새로운 열 “BMI”를 기존 매트릭스에 추가
print("5번. BMI 계산 후 데이터프레임:")
height_m = df["Height"] / 100  # cm → m 단위 변환
df["BMI"] = df["Weight"] / (height_m ** 2)
print(df)
print()

# 6번. BMI에 따라 비만도(Obesity)를 범주형으로 추가
print("6번. 비만도(Obesity) 범주 추가 후 데이터프레임:")
bins = [-np.inf, 18.5, 23, 25, 30, 34.9, np.inf]  # BMI 구간 기준
labels = ["Underweight", "Normal", "Overweight", "Obese1", "Obese2", "Obese3"]
df["Obesity"] = pd.cut(df["BMI"], bins=bins, labels=labels)
print(df)
print()

# 7번. Input과 Output 데이터 생성 (원핫 인코딩 포함)
print("7번. Input (X) 데이터:")
input_cols = ["Age", "HowLong", "Cigarettes", "Height", "Weight", "Waist", "Hips", "BMI"]
df_cat = pd.get_dummies(df[["Gender", "Smoker", "Obesity"]])  # 범주형 → 원핫 인코딩
X = pd.concat([df[input_cols], df_cat], axis=1)  # 수치형 + 인코딩 결합
print(X)
print()

print("7번. Output (y) 데이터:")
y = pd.get_dummies(df["Risk"])  # 다중 클래스 분류를 위한 원핫 인코딩
print(y)
print()

# 8번. 훈련/테스트 데이터 분리 (22% 테스트)
print("8번. 훈련/테스트 데이터 분리:")

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.22, random_state=42)

# 모델 학습을 위해 float32 타입으로 변환
X_train = np.asarray(X_train).astype(np.float32)
X_test = np.asarray(X_test).astype(np.float32)
y_train = np.asarray(y_train).astype(np.float32)
y_test = np.asarray(y_test).astype(np.float32)

print("X_train shape:", X_train.shape)
print("X_test shape:", X_test.shape)
print("y_train shape:", y_train.shape)
print("y_test shape:", y_test.shape)
print("dtype:", X_train.dtype)
print()

# 9번. 모델 생성 및 summary 호출
print("9번. 모델 구조 요약:")

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense

# 입력 레이어 (18차원)
inputs = Input(shape=(18,), name="input_20")

# 은닉층 1 (10개 뉴런, ReLU)
x = Dense(10, activation='relu')(inputs)

# 은닉층 2 (8개 뉴런, ReLU)
x = Dense(8, activation='relu')(x)

# 출력층 (3개 클래스, 소프트맥스)
outputs = Dense(3, activation='softmax')(x)

# 모델 정의
model = Model(inputs=inputs, outputs=outputs)
model.summary()
print()

# 10번. 모델 학습 (batch=√25, epoch=10)
print("10번. 모델 학습:")

from math import sqrt
batch_size = int(sqrt(25))  # 상수형 직접 입력 피하기 위해 sqrt 사용

# 모델 컴파일: 다중 클래스 분류용 손실 함수 사용
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# 모델 학습 (기본 로그 사용)
history = model.fit(
    X_train, y_train,
    batch_size=batch_size,
    epochs=10,
    validation_data=(X_test, y_test),
    verbose=1
)
print()

# 11번. 모델 평가
print("11번. 모델 평가:")
loss, accuracy = model.evaluate(X_test, y_test)
print("Loss:", loss)
print("Accuracy:", accuracy)
