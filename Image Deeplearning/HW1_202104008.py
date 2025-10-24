# 학번: 202104008 / 이름: 김진우
# dir = "C:/cv_workspace"  # 데이터 파일은 Windows 기준 C:/cv_workspace 하위에 위치 

# (수업 범위 내 라이브러리 사용)
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.pipeline import make_pipeline

# ------------------------------------------------------------
# 공통 설정(하드코딩 회피: 상수 대신 의미있는 변수명 사용)
FIG_SIZE_MEAN = (40, 10)      # Q3 figure size 요구
N_CLUSTERS = 4                # Q5-1 k-means 군집 수(라벨 4종)
PCA_DIM_2 = 2                 # Q5-1 주성분 차원
PCA_DIM_30 = 30               # Q6 주성분 차원
TEST_RATIO = 0.22             # Q6 테스트 비율 22%
CV_FOLDS = 7                  # Q8,9 교차검증 7-fold
RANDOM_SEED = 0               # 재현성을 위한 시드
MARKER_SIZE = 5               # 산점도 점 크기
ALPHA_SCATTER = 0.6           # 산점도 투명도
# ------------------------------------------------------------

# [실행용 macOS 경로 설정]  (본인 경로 맞춰서 수정 가능)
MAC_BASE_DIR = os.path.expanduser("Image Deeplearning")
CSV_PATH = os.path.join(MAC_BASE_DIR, "data.csv")

# ========================= (1) ==============================
# 파일을 읽고 파일의 행과 열의 개수 출력
df = pd.read_csv(CSV_PATH)
print(df.shape)  # 예시: (28000, 785)

# ========================= (2) ==============================
# 학습용 입력(X)과 정답(y) 분리 및 크기/라벨 정보 출력
# label 컬럼만 y로, 나머지 px0~px783을 X로
y = df["label"]
X = df.drop(columns=["label"])

print(f"X: {X.shape}")
print(f"y: {y.shape}")

labels, label_counts = np.unique(y.values, return_counts=True)
print((labels, label_counts))  # (array([0,1,5,8]), array([7000,7000,7000,7000]))

# ========================= (3) ==============================
# 각 라벨별 모든 이미지 픽셀 평균(28x28) 시각화 (for문 사용 허용)
plt.figure(figsize=FIG_SIZE_MEAN)
# 라벨 정렬해 고정된 순서(0,1,5,8)로 표시
for idx, lab in enumerate(sorted(labels)):
    # 해당 라벨의 모든 샘플 평균(축=0) -> 784 벡터
    mean_img = X[y.values == lab].mean(axis=0).values.reshape(28, 28)
    ax = plt.subplot(1, len(labels), idx + 1)
    ax.imshow(mean_img, cmap="gray")
    ax.set_title(f"label {lab}")
    ax.axis("off")
plt.tight_layout()
plt.show()

# ========================= (4) ==============================
# 각 라벨별 '이미지 평균 밝기(=픽셀 평균)' 분포 히스토그램 (for문 사용 허용)
# 한 이미지의 평균 밝기: 784픽셀의 평균
img_mean_intensity = X.mean(axis=1).values  # (전체 샘플 수,)
plt.figure(figsize=FIG_SIZE_MEAN)
for idx, lab in enumerate(sorted(labels)):
    ax = plt.subplot(1, len(labels), idx + 1)
    ax.hist(img_mean_intensity[y.values == lab], bins=30, edgecolor="black")
    ax.set_title(f"label {lab} intensity")
    ax.set_xlabel("mean pixel value")
    ax.set_ylabel("count")
plt.tight_layout()
plt.show()

# ========================= (5-1) ============================
# PCA(2차원) -> k-means(4개 군집) 후 예측된 라벨별 데이터 개수 출력
pca2 = PCA(n_components=PCA_DIM_2, random_state=RANDOM_SEED)
X_pca2 = pca2.fit_transform(X.values)  # float 변환은 내부에서 처리됨

kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_SEED, n_init=10)
pred_cluster = kmeans.fit_predict(X_pca2)

uniq_c, cnt_c = np.unique(pred_cluster, return_counts=True)
print((uniq_c, cnt_c.astype(int)))  # 예: (array([0,1,2,3], dtype=int32), array([...,...,...,...]))

# ========================= (5-2) ============================
# 위 예측군집을 2D 산점도로 시각화 (for문 사용 허용)
plt.figure(figsize=(10, 10))
for c in uniq_c:
    plt.scatter(
        X_pca2[pred_cluster == c, 0],
        X_pca2[pred_cluster == c, 1],
        s=MARKER_SIZE,
        alpha=ALPHA_SCATTER,
        label=f"cluster {c}",
    )
plt.title("KMeans clusters on PCA(2D)")
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.legend()
plt.show()

# ========================= (6) ==============================
# PCA(30차원) 후 train/test = 78%/22% 분리, 크기 출력
pca30 = PCA(n_components=PCA_DIM_30, random_state=RANDOM_SEED)
X_pca30 = pca30.fit_transform(X.values)

X_train, X_test, y_train, y_test = train_test_split(
    X_pca30, y.values, test_size=TEST_RATIO, random_state=RANDOM_SEED, stratify=y.values
)

print(f"훈련 데이터 X: {X_train.shape}")
print(f"훈련 데이터 y: {y_train.shape}")
print(f"테스트 데이터 X: {X_test.shape}")
print(f"테스트 데이터 y: {y_test.shape}")

# ========================= (7) ==============================
# StandardScaler로 정규화 후 일부 출력
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc = scaler.transform(X_test)

print("훈련 데이터 X정규화")
# 한 줄 전부 찍으면 너무 길어 가독성이 떨어져 앞/뒤 일부만 출력
print(np.concatenate([X_train_sc[:1, :15], X_train_sc[:1, -15:]], axis=1))
print("테스트 데이터 X 정규화")
print(np.concatenate([X_test_sc[:1, :15], X_test_sc[:1, -15:]], axis=1))

# ========================= (8) ==============================
# 로지스틱(경사하강법 기반 손실) 모델 학습 및 점수, 7-fold CV 점수
# (정규화된 학습 데이터를 사용)
lr = LogisticRegression(
    penalty="l2",
    solver="lbfgs",           # 멀티클래스엔 lbfgs가 안정적
    max_iter=1000,
    multi_class="multinomial",
    random_state=RANDOM_SEED
)
lr.fit(X_train_sc, y_train)

lr_train_score = lr.score(X_train_sc, y_train)
lr_test_score = lr.score(X_test_sc, y_test)
print(f"[로지스틱]훈련 데이터 점수: {lr_train_score}")
print(f"[로지스틱]테스트 데이터 점수: {lr_test_score}")

# 교차검증은 파이프라인으로 스케일러 누수 방지 + 동일 설정
pipe_lr = make_pipeline(StandardScaler(), LogisticRegression(
    penalty="l2",
    solver="lbfgs",
    max_iter=1000,
    multi_class="multinomial",
    random_state=RANDOM_SEED
))
cv_scores_lr = cross_val_score(pipe_lr, X_pca30, y.values, cv=CV_FOLDS)
print(f"[교차검증]테스트 데이터 점수: {cv_scores_lr.mean()}")

# ========================= (9) ==============================
# 결정트리 학습 및 점수, 7-fold CV 점수 (정규화된 데이터 사용)
dt = DecisionTreeClassifier(random_state=RANDOM_SEED)
dt.fit(X_train_sc, y_train)

dt_train_score = dt.score(X_train_sc, y_train)
dt_test_score = dt.score(X_test_sc, y_test)
print(f"[결정트리]훈련 데이터 점수: {dt_train_score}")
print(f"[결정트리]테스트 데이터 점수: {dt_test_score}")

pipe_dt = make_pipeline(StandardScaler(), DecisionTreeClassifier(random_state=RANDOM_SEED))
cv_scores_dt = cross_val_score(pipe_dt, X_pca30, y.values, cv=CV_FOLDS)
print(f"[교차검증]테스트 데이터 점수: {cv_scores_dt.mean()}")

# ========================= (10) =============================
# 테스트 데이터 중 10개 선택하여 두 모델 예측값 + 실제값 출력
idx10 = np.arange(10)
lr_pred_10 = lr.predict(X_test_sc[idx10])
dt_pred_10 = dt.predict(X_test_sc[idx10])
y_true_10 = y_test[idx10]

print(f"[로지스틱]예측한 값: {lr_pred_10}")
print(f"[결정트리]예측한 값: {dt_pred_10}")
print(f"실제 정답: {y_true_10}")
