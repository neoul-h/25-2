# -*- coding: utf-8 -*-
"""
파일 이름: week04_cluster_annotated.py

무엇을 하나요?
- 과일(사과/파인애플/바나나) 100x100 흑백 이미지 300장을 불러와서
  (1) 평균/히스토그램/절대차 등 기초 분석
  (2) K-평균(KMeans)으로 3개 무리(클러스터)로 자동 묶기
  (3) PCA(주성분분석)로 차원 축소/복원/시각화
  (4) 로지스틱 회귀로 분류 정확도 비교(원본 vs PCA축소)
을 연습합니다.

필요 파일: fruits_300.npy (경로: C:/cv_workspace/data/fruits_300.npy)
- 없으면 경로를 내 PC에 맞게 수정하세요.
"""

import numpy as np
import matplotlib.pyplot as plt

# -------------------------------
# 1) 데이터 불러오기 + 모양 확인
# -------------------------------
try:
    fruits = np.load('C:/cv_workspace/data/fruits_300.npy')
    print(fruits.shape)  # 예상 출력: (300, 100, 100) = 300장, 100x100 픽셀
    print(fruits[0, 0, :])  # 첫 이미지의 첫 줄 픽셀들 (예시: 0~255 값들)
except Exception as e:
    print("[참고] fruits_300.npy 파일을 찾지 못했습니다. 경로를 확인하세요.", e)
    fruits = None

if fruits is not None:
    plt.imshow(fruits[0], cmap='gray'); plt.title('fruits[0]'); plt.show()

    # 여러 장 비교(색 반전 colormap gray_r로 모양 확인)
    fig, axs = plt.subplots(1, 2)
    axs[0].imshow(fruits[100], cmap='gray_r'); axs[0].set_title('fruits[100]')
    axs[1].imshow(fruits[200], cmap='gray_r'); axs[1].set_title('fruits[200]')
    for ax in axs: ax.set_xticks([]); ax.set_yticks([])
    plt.show()

    # -------------------------------
    # 2) 평균/히스토그램으로 비교
    # -------------------------------
    # 이미지 100장을 한 줄(10000픽셀)로 펴서 평균 등을 계산
    apple     = fruits[0:100].reshape(-1, 100*100)
    pineapple = fruits[100:200].reshape(-1, 100*100)
    banana    = fruits[200:300].reshape(-1, 100*100)

    print(apple.mean(axis=1))  # 각 사과 이미지의 평균 밝기(예: 0~255 사이)

    # 히스토그램: 과일별 평균 밝기 분포 비교
    plt.hist(np.mean(apple, axis=1), alpha=0.8)
    plt.hist(np.mean(pineapple, axis=1), alpha=0.8)
    plt.hist(np.mean(banana, axis=1), alpha=0.8)
    plt.legend(['apple', 'pineapple', 'banana'])
    plt.title('이미지 평균 밝기 분포'); plt.show()

    # 픽셀 위치(0~9999)별 평균 밝기 막대 그래프
    fig, axs = plt.subplots(1, 3, figsize=(20,5))
    axs[0].bar(range(10000), np.mean(apple, axis=0));     axs[0].set_title('apple mean')
    axs[1].bar(range(10000), np.mean(pineapple, axis=0)); axs[1].set_title('pineapple mean')
    axs[2].bar(range(10000), np.mean(banana, axis=0));    axs[2].set_title('banana mean')
    for ax in axs: ax.set_xticks([])
    plt.show()

    # 평균 이미지로 시각화
    apple_mean     = np.mean(apple, axis=0).reshape(100, 100)
    pineapple_mean = np.mean(pineapple, axis=0).reshape(100, 100)
    banana_mean    = np.mean(banana, axis=0).reshape(100, 100)
    fig, axs = plt.subplots(1, 3, figsize=(20,5))
    axs[0].imshow(apple_mean, cmap='gray_r');     axs[0].set_title('apple mean')
    axs[1].imshow(pineapple_mean, cmap='gray_r'); axs[1].set_title('pineapple mean')
    axs[2].imshow(banana_mean, cmap='gray_r');    axs[2].set_title('banana mean')
    for ax in axs: ax.set_xticks([]); ax.set_yticks([])
    plt.show()

    # 절대차 평균으로 "사과스러움" 점수 구해보기: apple_mean과 가까운 것을 골라봄
    abs_diff = np.abs(fruits - apple_mean)
    abs_mean = np.mean(abs_diff, axis=(1,2))
    print(abs_mean.shape)  # 예상: (300,)
    apple_index = np.argsort(abs_mean)[:100]  # apple_mean과 가장 비슷한 100장

    def draw_fruits(arr, ratio=1):
        n = len(arr)
        rows = int(np.ceil(n/10))
        cols = n if rows < 2 else 10
        fig, axs = plt.subplots(rows, cols, figsize=(cols*ratio, rows*ratio), squeeze=False)
        for i in range(rows):
            for j in range(cols):
                if i*10 + j < n:
                    axs[i, j].imshow(arr[i*10 + j], cmap='gray_r')
                axs[i, j].axis('off')
        plt.show()

    fig, axs = plt.subplots(10, 10, figsize=(10,10))
    for i in range(10):
        for j in range(10):
            axs[i, j].imshow(fruits[apple_index[i*10 + j]], cmap='gray_r')
            axs[i, j].axis('off')
    plt.suptitle('apple-like top100'); plt.show()

    # -------------------------------
    # 3) K-평균(KMeans)으로 3개 군집 찾기
    # -------------------------------
    fruits_2d = fruits.reshape(-1, 100*100)

    from sklearn.cluster import KMeans
    km = KMeans(n_clusters=3, random_state=42)
    km.fit(fruits_2d)

    print(km.labels_)  # 각 이미지가 속한 클러스터 번호(0/1/2)
    print(np.unique(km.labels_, return_counts=True))  # 각 클러스터에 몇 장씩?

    draw_fruits(fruits[km.labels_==0]); print("\n")
    draw_fruits(fruits[km.labels_==1]); print("\n")
    draw_fruits(fruits[km.labels_==2]); print("\n")

    # 클러스터 "중심"을 그림으로 보기
    draw_fruits(km.cluster_centers_.reshape(-1, 100, 100), ratio=3)

    # 특정 샘플과 중심거리(변환값) & 예측 클러스터
    print(km.transform(fruits_2d[100:101]))  # 3개 중심까지의 거리
    print(km.predict(fruits_2d[100:101]))    # 속한 클러스터 번호
    draw_fruits(fruits[100:101])             # 실제 이미지 확인
    print(km.n_iter_)                        # 반복 학습 횟수

    # 클러스터 수(k)에 따른 관성(inertia) 비교(엘보우 기법 느낌)
    inertia = []
    for k in range(2, 7):
        km = KMeans(n_clusters=k, random_state=42)
        km.fit(fruits_2d)
        inertia.append(km.inertia_)
    plt.plot(range(2, 7), inertia); plt.title('inertia vs k'); plt.show()

    # -------------------------------
    # 4) PCA(주성분분석) 차원 축소/복원
    # -------------------------------
    from sklearn.decomposition import PCA
    pca = PCA(n_components=50)
    pca.fit(fruits_2d)
    print(pca.components_.shape)  # (50, 10000)

    draw_fruits(pca.components_.reshape(-1, 100, 100))

    print(fruits_2d.shape)  # (300, 10000)
    fruits_pca = pca.transform(fruits_2d)
    print(fruits_pca.shape) # (300, 50)

    fruits_inverse = pca.inverse_transform(fruits_pca)
    print(fruits_inverse.shape) # (300, 10000)
    fruits_reconstruct = fruits_inverse.reshape(-1, 100, 100)
    for start in [0, 100, 200]:
        draw_fruits(fruits_reconstruct[start:start+100]); print("\n")

    print(np.sum(pca.explained_variance_ratio_))  # 보존된 분산 비율(예: 0.9~0.99)
    plt.plot(pca.explained_variance_ratio_); plt.title('설명분산비율'); plt.show()

    # -------------------------------
    # 5) 분류 성능(로지스틱) - 원본 vs PCA
    # -------------------------------
    from sklearn.linear_model import LogisticRegression
    lr = LogisticRegression(max_iter=1000)

    target = np.array([0]*100 + [1]*100 + [2]*100)  # 간단한 정답: 0사과,1파인애플,2바나나
    from sklearn.model_selection import cross_validate
    scores = cross_validate(lr, fruits_2d, target)
    print(np.mean(scores['test_score']))  # 예: 0.9~1.0
    print(np.mean(scores['fit_time']))    # 학습 시간

    scores = cross_validate(lr, fruits_pca, target)
    print(np.mean(scores['test_score']))  # 예: 거의 비슷하거나 살짝 감소
    print(np.mean(scores['fit_time']))    # 보통 더 빨라짐

    # 주성분 개수를 "비율"로 지정해서 자동 선택
    pca = PCA(n_components=0.5)
    pca.fit(fruits_2d)
    print(pca.n_components_)     # 선택된 주성분 수
    fruits_pca = pca.transform(fruits_2d)
    print(fruits_pca.shape)

    scores = cross_validate(lr, fruits_pca, target)
    print(np.mean(scores['test_score']))
    print(np.mean(scores['fit_time']))

    # PCA 축소 후 다시 KMeans로 묶기
    km = KMeans(n_clusters=3, random_state=42)
    km.fit(fruits_pca)
    print(np.unique(km.labels_, return_counts=True))

    for label in range(0, 3):
        draw_fruits(fruits[km.labels_ == label]); print("\n")

    # 2차원만 골라서 산점도로 군집 확인(시각화)
    for label in range(0, 3):
        data = fruits_pca[km.labels_ == label]
        plt.scatter(data[:,0], data[:,1])
    plt.legend(['apple', 'banana', 'pineapple'])
    plt.title('PCA 2D scatter by cluster')
    plt.show()

# 끝!
