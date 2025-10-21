# -*- coding: utf-8 -*-
"""
HW1_학번.py  (복붙 제출용)

[과목] 2025-2 이미지 딥러닝 Homework  (문항 1~10 전부 해결)
[데이터] C:/cv_workspace/data.csv  (28,000행 × 785열: 픽셀 784 + label 1)
[지시 준수]
- for문/if문 금지(단, 문제 3,4,5-2는 for문 사용 가능)  -> 해당 문항에만 for문 사용함
- 상수형 숫자 직접 계산 금지(평균 등을 90/40처럼 계산 X) -> 모두 함수 사용
- 사용 라이브러리: pandas, numpy, matplotlib, scikit-learn (수업에서 다룬 범위 내)
- 출력형식: 문제에서 요구한 문구/형식 최대한 동일하게 맞춤
- 주석: 중학생도 이해할 수 있게 상세 주석

[제출 전 메모]
- 아래 "학번/이름"을 본인 정보로 바꾸세요.
"""

# ─────────────────────────────────────────────────────────────────────────────
# [학번/이름]
# 학번: 20XX0000
# 이름: 홍길동
# ─────────────────────────────────────────────────────────────────────────────

# 공통 라이브러리 불러오기
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 기계학습 도구들 (문항 5~9에서 사용)
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import SGDClassifier
from sklearn.tree import DecisionTreeClassifier

# 보기 좋게 출력(너무 긴 배열은 줄바꿈)
np.set_printoptions(suppress=True, linewidth=120)

# 데이터 경로(과제 규정: C:/cv_workspace 하위)
DIR = "C:/cv_workspace"
DATA_PATH = f"{DIR}/data.csv"

# =============================================================================
# (3점) 1. 파일을 읽고 파일의 행과 열의 개수를 출력
# =============================================================================
# - pd.read_csv로 CSV를 읽어 DataFrame(df)으로 만든다.
# - df.shape는 (행 개수, 열 개수)를 튜플로 준다.
df = pd.read_csv(DATA_PATH)

print(df.shape)
# 예상실행결과(예시)
# (28000, 785)

# =============================================================================
# (7점) 2. X(입력)와 y(정답) 분리 후, 각 데이터의 행/열 출력
#         그리고 y의 라벨 종류와 각 클래스별 개수 출력
# =============================================================================
# - 입력 X: 픽셀(px0 ~ px783) 784개 열
# - 정답 y: label 열
# - 열 선택은 drop 또는 filter를 사용 (둘 다 수업에서 다룬 방식)
X = df.drop(columns=["label"]).values      # 넘파이 배열(모델 학습에 적합)
y = df["label"].values                     # 넘파이 배열(정답 라벨)

print("X:", X.shape)                       # (행, 열)
print("y:", y.shape)                       # (행,)
print(np.unique(y, return_counts=True))    # (라벨종류 배열, 각 개수 배열)

# 예상실행결과(예시)
# X: (28000, 784)
# y: (28000,)
# (array([0, 1, 5, 8]), array([7000, 7000, 7000, 7000]))

# =============================================================================
# (13점) 3. 각 라벨별로 모든 이미지의 "픽셀값 평균"을 28×28로 출력
#   - figure 사이즈: 가로 40, 세로 10
#   - for문 사용 가능
# =============================================================================
# - 라벨이 같은 이미지들만 모아(불리언 인덱싱), 행 방향 평균(axis=0)으로 픽셀별 평균을 구한다.
# - 평균 벡터(784)를 reshape(28,28)해서 그림으로 본다(흑백).
labels_sorted = np.unique(y)  # array([0,1,5,8])

plt.figure(figsize=(40, 10))  # 가로 40, 세로 10 (과제 지시)
for idx, lab in enumerate(labels_sorted):   # ← 문항 3은 for문 허용
    mean_img = X[y == lab].mean(axis=0).reshape(28, 28)  # 픽셀별 평균 → 28x28
    ax = plt.subplot(1, len(labels_sorted), idx + 1)
    ax.imshow(mean_img, cmap="gray")
    ax.set_title(f"label {lab} 평균 이미지", fontsize=16)
    ax.axis("off")
plt.suptitle("문제 3) 라벨별 픽셀 평균 (28x28)", fontsize=20)
plt.tight_layout()
plt.show()

# =============================================================================
# (12점) 4. 각 라벨별로 "개별 이미지의 평균 픽셀값" 분포 히스토그램
#   - for문 사용 가능
# =============================================================================
# - 각 행(이미지)마다 평균을 구해 1개 값(스칼라)로 만든 뒤, 라벨별 히스토그램을 그린다.
plt.figure(figsize=(24, 6))
for idx, lab in enumerate(labels_sorted):   # ← 문항 4는 for문 허용
    # y==lab인 행들에 대해, 각 행의 평균값(픽셀 784개의 평균)을 계산 → 1D(샘플 수,)
    per_image_means = X[y == lab].mean(axis=1)
    ax = plt.subplot(1, len(labels_sorted), idx + 1)
    ax.hist(per_image_means, bins=30, alpha=0.85)
    ax.set_title(f"label {lab} 평균픽셀 히스토그램", fontsize=14)
    ax.set_xlabel("평균 밝기")
    ax.set_ylabel("빈도")
plt.suptitle("문제 4) 라벨별 이미지 평균 픽셀값 분포", fontsize=18)
plt.tight_layout()
plt.show()

# =============================================================================
# (10점) 5-1. PCA로 2차원 축소 → k-평균(k=4) 군집 → 군집별 데이터 개수 출력
# =============================================================================
# - 비지도 학습: 정답 y를 쓰지 않고 X만 사용
# - PCA(n_components=2)로 차원 축소 후 KMeans(n_clusters=4)
pca2 = PCA(n_components=2, random_state=42)
X_pca2 = pca2.fit_transform(X)                 # (28000, 2)

kmeans4 = KMeans(n_clusters=4, n_init="auto", random_state=42)
pred_cluster = kmeans4.fit_predict(X_pca2)     # (28000,)

print(np.unique(pred_cluster, return_counts=True))
# 예상실행결과(예시 / 다를 수 있음)
# (array([0, 1, 2, 3], dtype=int32), array([8807, 8700, 4613, 5880]))

# =============================================================================
# (7점) 5-2. 위 예측 라벨(군집)로 PCA 2D 산점도 시각화
#   - for문 사용 가능
# =============================================================================
plt.figure(figsize=(8, 6))
unique_cl = np.unique(pred_cluster)
for c in unique_cl:                           # ← 문항 5-2는 for문 허용
    pts = X_pca2[pred_cluster == c]
    plt.scatter(pts[:, 0], pts[:, 1], s=2, alpha=0.5, label=f"cluster {c}")
plt.title("문제 5-2) PCA(2D) + KMeans(4) 클러스터 시각화")
plt.xlabel("PC1"); plt.ylabel("PC2")
plt.legend()
plt.tight_layout()
plt.show()

# =============================================================================
# (10점) 6. PCA 30차원 축소 → 테스트 22%로 분리 → 각 데이터의 행/열 출력
# =============================================================================
# - train_test_split에서 test_size=0.22 (과제 지시)
# - stratify=y를 주면 클래스 비율이 유지되어 더 안정적(선택사항), 규정 위반 아님
pca30 = PCA(n_components=30, random_state=42)
X_pca30 = pca30.fit_transform(X)              # (28000, 30)

X_train, X_test, y_train, y_test = train_test_split(
    X_pca30, y, test_size=0.22, random_state=42, stratify=y
)

print("훈련 데이터 X:", X_train.shape)
print("훈련 데이터 y:", y_train.shape)
print("테스트 데이터 X:", X_test.shape)
print("테스트 데이터 y:", y_test.shape)
# 예상실행결과(예시)
# 훈련 데이터 X: (21840, 30)
# 훈련 데이터 y: (21840,)
# 테스트 데이터 X: (6160, 30)
# 테스트 데이터 y: (6160,)

# =============================================================================
# (10점) 7. StandardScaler 정규화 후 일부 출력
# =============================================================================
# - 평균 0, 표준편차 1이 되도록 맞춘다(학습 데이터 기준으로 학습→둘 다 변환)
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

print("훈련 데이터 X 정규화")
print(X_train_sc[:1])  # 첫 1행만 출력 (보기 예시와 달라도 정상)
print("\n테스트 데이터 X 정규화")
print(X_test_sc[:1])   # 첫 1행만 출력

# 예상실행결과(예시 / 값은 환경마다 다를 수 있음)
# 훈련 데이터 X정규화
# [[ 0.39844136 -1.19690862 -0.76823836 ...  0.23280841 -1.40834924]]
#
# 테스트 데이터 X 정규화
# [[-1.56465423e+00 -2.01430248e-01  3.15075158e-01 ...  5.97728327e-01 -7.50838473e-01]]

# =============================================================================
# (10점) 8. 로지스틱 손실의 경사 하강법(SGDClassifier) 학습/평가 + 7폴드 CV
# =============================================================================
# - 수업에서 다룬 SGDClassifier 사용 (loss='log_loss'가 로지스틱 손실)
logi = SGDClassifier(loss="log_loss", max_iter=1000, random_state=42)
logi.fit(X_train_sc, y_train)

train_score_logi = logi.score(X_train_sc, y_train)
test_score_logi  = logi.score(X_test_sc, y_test)
print("[로지스틱]훈련 데이터 점수:", train_score_logi)
print("[로지스틱]테스트 데이터 점수:", test_score_logi)

# 7폴드 교차검증 (학습 데이터에 대해 교차검증을 수행하고 평균 테스트 점수 출력)
cv_res_logi = cross_validate(logi, X_train_sc, y_train, cv=7, n_jobs=-1, return_train_score=False)
cv_mean_logi = np.mean(cv_res_logi["test_score"])
print("[교차검증]테스트 데이터 점수:", cv_mean_logi)

# 예상실행결과(예시 / 다를 수 있음)
# [로지스틱]훈련 데이터 점수: 0.9736...
# [로지스틱]테스트 데이터 점수: 0.9696...
# [교차검증]테스트 데이터 점수: 0.9729...

# =============================================================================
# (10점) 9. 결정트리 학습/평가 + 7폴드 CV (정규화된 데이터 사용)
# =============================================================================
# - 결정트리는 스케일에 덜 민감하지만, 과제 지시는 "정규화된 학습 데이터를 이용" → 그대로 따름
dt = DecisionTreeClassifier(random_state=42)
dt.fit(X_train_sc, y_train)

train_score_dt = dt.score(X_train_sc, y_train)
test_score_dt  = dt.score(X_test_sc, y_test)
print("[결정트리]훈련 데이터 점수:", train_score_dt)
print("[결정트리]테스트 데이터 점수:", test_score_dt)

cv_res_dt = cross_validate(dt, X_train_sc, y_train, cv=7, n_jobs=-1, return_train_score=False)
cv_mean_dt = np.mean(cv_res_dt["test_score"])
print("[교차검증]테스트 데이터 점수:", cv_mean_dt)

# 예상실행결과(예시 / 다를 수 있음)
# [결정트리]훈련 데이터 점수: 1.0
# [결정트리]테스트 데이터 점수: 0.9599...
# [교차검증]테스트 데이터 점수: 0.9562...

# =============================================================================
# (8점) 10. 테스트 데이터 중 10개를 뽑아 예측값(두 모델)과 실제값 함께 출력
# =============================================================================
# - 앞에서 만든 정규화된 X_test_sc, y_test 사용
idx10 = np.arange(10)                   # 앞에서부터 10개 인덱스
pred10_logi = logi.predict(X_test_sc[idx10])
pred10_dt   = dt.predict(X_test_sc[idx10])
real10      = y_test[idx10]

print("[로지스틱]예측한 값:", pred10_logi.tolist())
print("[결정트리]예측한 값:", pred10_dt.tolist())
print("실제 정답:", real10.tolist())

# 예상실행결과(예시 / 다를 수 있음)
# [로지스틱]예측한 값: [5, 0, 5, 8, 8, 0, 5, 0, 8, 0]
# [결정트리]예측한 값: [5, 0, 5, 8, 8, 0, 5, 0, 8, 0]
# 실제 정답:     [5, 0, 5, 8, 8, 0, 5, 0, 8, 0]

# ─────────────────────────────────────────────────────────────────────────────
# 끝. 수고했어요! (그래프는 실행 시 팝업 창으로 표시됩니다)
# ─────────────────────────────────────────────────────────────────────────────
