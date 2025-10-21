# -*- coding: utf-8 -*-
"""
[중학생도 이해할 수 있는 쉬운 설명 + 전체 주석판]
파일 이름: week02_Regression_annotated.py

무엇을 하나요?
- 농어(perch) 길이를 입력하면 무게를 예측하는 "머신러닝 회귀(regression)" 실습입니다.
- k-최근접 이웃(KNN) 회귀 / 선형 회귀(직선) / 다항회귀(곡선) / 규제회귀(Ridge, Lasso)까지
  차근차근 경험합니다.
- 마지막에는 분류(LogisticRegression, SGDClassifier) 예제도 살짝 체험합니다.

어떻게 읽으면 좋을까요?
1) 작은 덩어리(블록) 단위로 나눠 주석을 달았습니다.
2) 각 print() 옆에 "예상 출력(예시)"를 주석으로 적었습니다. (환경에 따라 조금씩 달라도 정상)
3) 윈도우 경로(C:/cv_workspace/...)는 본인 PC 경로에 맞게 바꿔주세요.

필요 라이브러리:
- numpy, matplotlib, scikit-learn(sklearn), pandas, scipy
- 설치: pip install numpy matplotlib scikit-learn pandas scipy
"""

# -------------------------------
# 0. 기본 준비: 라이브러리 로드
# -------------------------------
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------
# 1. (데이터 준비) 농어 길이와 무게
# -------------------------------
# - 아래 두 배열은 실측한 '농어의 길이'와 '무게'입니다.
# - 길이가 길수록(대체로) 무게가 커지겠죠? 이 패턴을 모델이 배우도록 합니다.
perch_length = np.array(
[ 8.4, 13.7, 15.0, 16.2, 17.4, 18.0, 18.7, 19.0, 19.6, 20.0,
  21.0, 21.0, 21.0, 21.3, 22.0, 22.0, 22.0, 22.0, 22.0, 22.5,
  22.5, 22.7, 23.0, 23.5, 24.0, 24.0, 24.6, 25.0, 25.6, 26.5,
  27.3, 27.5, 27.5, 27.5, 28.0, 28.7, 30.0, 32.8, 34.5, 35.0,
  36.5, 36.0, 37.0, 37.0, 39.0, 39.0, 39.0, 40.0, 40.0, 40.0,
  40.0, 42.0, 43.0, 43.0, 43.5, 44.0]
)
perch_weight = np.array(
[   5.9,  32.0,  40.0,  51.5,  70.0, 100.0,  78.0,  80.0,  85.0,  85.0,
  110.0, 115.0, 125.0, 130.0, 120.0, 120.0, 130.0, 135.0, 110.0, 130.0,
  150.0, 145.0, 150.0, 170.0, 225.0, 145.0, 188.0, 180.0, 197.0, 218.0,
  300.0, 260.0, 265.0, 250.0, 250.0, 300.0, 320.0, 514.0, 556.0, 840.0,
  685.0, 700.0, 700.0, 690.0, 900.0, 650.0, 820.0, 850.0, 900.0, 1015.0,
  820.0, 1100.0, 1000.0, 1100.0, 1000.0, 1000.0]
)

# (보기) 산점도: x축=길이, y축=무게. 점들이 오른쪽 위로 갈수록 무게가 커짐을 볼 수 있어요.
plt.scatter(perch_length, perch_weight)
plt.xlabel('length (cm)')
plt.ylabel('weight (g)')
plt.title('Perch length vs. weight (산점도)')
plt.show()

# scikit-learn에 넣기 위해 (샘플 수, 특성 수) 2차원 모양으로 바꿔요.
# 지금은 길이 1개 특성뿐이니 특성 수 = 1
perch_length = perch_length.reshape(-1, 1)
perch_weight = perch_weight.reshape(-1, 1)

# -------------------------------
# 2. 훈련/테스트 데이터 나누기
# -------------------------------
from sklearn.model_selection import train_test_split

train_input, test_input, train_target, test_target = train_test_split(
    perch_length, perch_weight, random_state=42
)
# train_* : 모델이 배우는 데이터(75% 정도), test_* : 모델을 마지막에 시험보는 데이터(25% 정도)

# -------------------------------
# 3. K-최근접 이웃(KNN) 회귀
# -------------------------------
from sklearn.neighbors import KNeighborsRegressor
knr = KNeighborsRegressor()  # 기본 k=5 (주변 점 5개 평균으로 예측)

# (학습) 길이->무게 관계를 훈련 데이터에서 배웁니다.
knr.fit(train_input, train_target)

# (평가1) 평균 절댓값 오차(MAE): 실제무게와 예측무게 차이를 절대값으로 평균
from sklearn.metrics import mean_absolute_error
test_prediction = knr.predict(test_input)
mae = mean_absolute_error(test_target, test_prediction)
print(mae)  # 예상 출력(예시): 약 19~40 사이 (데이터 분할/버전에 따라 조금 차이)
print(knr.score(test_input, test_target))   # 결정계수 R^2 (1.0에 가까울수록 좋음)
print(knr.score(train_input, train_target)) # 훈련 점수

# (하이퍼파라미터 바꾸기) k를 3으로 줄여봅니다. (더 가까운 소수의 이웃만 봄)
knr.n_neighbors = 3
knr.fit(train_input, train_target)
print(knr.score(train_input, train_target))  # 훈련 점수 (예: 더 높아질 수 있음)
print(knr.score(test_input, test_target))    # 테스트 점수 (너무 작게 하면 과적합 위험)

# 이웃 시각화: 길이 50cm 농어 주변의 3개 이웃을 찍어보기
distances, indexes = knr.kneighbors([[50]])  # 50cm에 가장 가까운 훈련 샘플 3개
plt.scatter(train_input, train_target, label='train')
plt.scatter(train_input[indexes], train_target[indexes], marker='D', label='neighbors')
plt.scatter(50, 1033, marker='^', label='(가상의) 50cm, 1033g')
plt.legend(); plt.title('50cm 이웃 시각화')
plt.show()

# 이웃들의 평균 무게(=KNN 예측값 근사)
print(np.mean(train_target[indexes]))  # 예상 출력(예시): 약 1000 전후의 값

# 길이 100cm라면? (실제 데이터 범위를 벗어나므로 KNN은 근처 이웃 평균이라 신뢰도 낮음)
print(knr.predict([[100]]))  # 예상 출력(예시): 약 1000 전후 (이웃 평균 때문에)

# 100cm 이웃도 확인
distances, indexes = knr.kneighbors([[100]])
plt.scatter(train_input, train_target, label='train')
plt.scatter(train_input[indexes], train_target[indexes], marker='D', label='neighbors@100')
plt.scatter(100, 1033, marker='^', label='(가상의) 100cm')
plt.legend(); plt.title('100cm 이웃 시각화')
plt.show()

# -------------------------------
# 4. 선형 회귀 (직선 y = ax + b)
# -------------------------------
from sklearn.linear_model import LinearRegression
lr = LinearRegression()
lr.fit(train_input, train_target)

print(lr.predict([[50]]))       # 50cm 예측값 (예시: 대략 1000~1600 근처)
print(lr.coef_, lr.intercept_)  # 기울기 a, 절편 b

# 직선을 같이 그려보기
plt.scatter(train_input, train_target)
# 15~50 구간 직선 (참고: 아래는 학습된 a,b를 직접 써도 되고 계산해도 됩니다)
x1, x2 = 15, 50
y1 = x1*lr.coef_[0] + lr.intercept_[0]
y2 = x2*lr.coef_[0] + lr.intercept_[0]
plt.plot([x1, x2], [y1, y2])
plt.scatter(50, 1241.8, marker='^', label='(참고) 50cm 예시표시')
plt.title('선형 회귀 직선')
plt.legend(); plt.show()

print(lr.score(train_input, train_target))  # 훈련 R^2
print(lr.score(test_input, test_target))    # 테스트 R^2

# -------------------------------
# 5. 다항 회귀 (2차 곡선)
# -------------------------------
# 길이^2, 길이 두 개의 특성을 넣어 직선 모델로 '곡선'을 표현
train_poly = np.column_stack((train_input ** 2, train_input))
test_poly  = np.column_stack((test_input ** 2,  test_input))
print(train_poly.shape, test_poly.shape)  # 예상 출력: (42,2) (14,2) 정도

lr = LinearRegression()
lr.fit(train_poly, train_target)
print(lr.predict([[50**2, 50]]))  # 50cm 예측(예시: 직선보다 더 현실적)

print(lr.coef_, lr.intercept_)    # 2차항, 1차항의 계수, 절편

# 2차 곡선 모양 그리기
point = np.arange(15, 51)
plt.scatter(train_input, train_target)
# 아래 그래프식은 책/강의 예시 곡선 (학습 결과와 유사한 참고용)
plt.plot(point, 1.01*point**2 - 21.6*point + 116.05)
plt.scatter(50, 1574, marker='^', label='(참고) 50cm 예시표시')
plt.title('2차 다항 회귀 곡선')
plt.legend(); plt.show()

print(lr.score(train_poly, train_target))  # 훈련 R^2
print(lr.score(test_poly, test_target))    # 테스트 R^2

# -------------------------------
# 6. (확장) 여러 특성을 자동으로 만들고 규제(Ridge/Lasso) 적용
# -------------------------------
import pandas as pd
# NOTE: 아래 파일 경로는 본인 PC에 파일이 있어야 합니다.
# 예) perch_full.csv: 길이/높이/폭 등 여러 특성 포함된 데이터셋
# 경로가 다르면 'C:/cv_workspace/data/perch_full.csv'를 내 경로로 바꾸세요.
try:
    perch_full = pd.read_csv('C:/cv_workspace/data/perch_full.csv')
    print(perch_full.head())  # 예상 출력: 상위 5행이 표로 출력
except Exception as e:
    print("[참고] perch_full.csv 를 못 찾았습니다. 경로를 내 PC에 맞춰 수정하세요.", e)

# 타깃(정답) 무게(y)
perch_weight = np.array(
[ 5.9, 32.0, 40.0, 51.5, 70.0, 100.0, 78.0, 80.0, 85.0, 85.0,
  110.0, 115.0, 125.0, 130.0, 120.0, 120.0, 130.0, 135.0, 110.0,
  130.0, 150.0, 145.0, 150.0, 170.0, 225.0, 145.0, 188.0, 180.0,
  197.0, 218.0, 300.0, 260.0, 265.0, 250.0, 250.0, 300.0, 320.0,
  514.0, 556.0, 840.0, 685.0, 700.0, 700.0, 690.0, 900.0, 650.0,
  820.0, 850.0, 900.0, 1015.0, 820.0, 1100.0, 1000.0, 1100.0,
  1000.0, 1000.0]
)

# (특성 만들기) PolynomialFeatures: 기존 특성들로 제곱/곱 등 새로운 특성 생성
from sklearn.preprocessing import PolynomialFeatures
poly = PolynomialFeatures()
poly.fit([[2, 3]])
print(poly.transform([[2, 3]]))  # 예상 출력: [[1. 2. 3. 4. 6. 9.]] (상수/각항/곱/제곱)

poly = PolynomialFeatures(include_bias=False)  # 상수항(1) 제외
poly.fit([[2, 3]])
print(poly.transform([[2, 3]]))  # 예상 출력: [[2. 3. 4. 6. 9.]]

# (여러 특성 변환) perch_full DataFrame에 대해 다항특성 만들기
try:
    poly = PolynomialFeatures(include_bias=False)
    poly.fit(perch_full)
    X = poly.transform(perch_full)
    print(X.shape)  # 예: (샘플수, 새로만든 특성 수)
except Exception:
    X = None
    print("[참고] perch_full.csv 가 없어 X를 만들지 못했습니다.")

from sklearn.model_selection import train_test_split
if X is not None:
    train_input, test_input, train_target, test_target = train_test_split(
        X, perch_weight, random_state=42
    )
    from sklearn.linear_model import LinearRegression
    lr = LinearRegression()
    lr.fit(train_input, train_target)
    print(lr.score(train_input, train_target))  # 훈련 R^2
    print(lr.score(test_input, test_target))    # 테스트 R^2

    # (더 많은 차수) degree=5: 더 복잡한 곡선도 표현 가능 (과적합 주의)
    poly = PolynomialFeatures(degree=5, include_bias=False)
    poly.fit(perch_full)
    X2 = poly.transform(perch_full)
    print(X2.shape)  # 예상: 특성 수가 많이 늘어남

    train_input, test_input, train_target, test_target = train_test_split(
        X2, perch_weight, random_state=42
    )
    lr = LinearRegression()
    lr.fit(train_input, train_target)
    print(lr.score(train_input, train_target))
    print(lr.score(test_input, test_target))

    # (규제) 표준화 후 Ridge/Lasso로 과적합 완화
    from sklearn.preprocessing import StandardScaler
    ss = StandardScaler()
    ss.fit(train_input)
    train_scaled = ss.transform(train_input)
    test_scaled  = ss.transform(test_input)

    from sklearn.linear_model import Ridge
    ridge = Ridge(alpha=1.0)  # 규제 세기(클수록 계수 더 작게 만듦)
    ridge.fit(train_scaled, train_target)
    print(ridge.score(train_scaled, train_target))
    print(ridge.score(test_scaled, test_target))

    # alpha별 성능 확인 (로그축으로 그리면 보기 편함)
    train_score, test_score = [], []
    alpha_list = [0.001, 0.01, 0.1, 1, 10, 100]
    for alpha in alpha_list:
        ridge = Ridge(alpha=alpha)
        ridge.fit(train_scaled, train_target)
        train_score.append(ridge.score(train_scaled, train_target))
        test_score.append(ridge.score(test_scaled, test_target))
    plt.plot(np.log10(alpha_list), train_score, label='train R^2')
    plt.plot(np.log10(alpha_list), test_score,  label='test R^2')
    plt.xlabel('log10(alpha)'); plt.ylabel('R^2'); plt.legend(); plt.show()

    ridge = Ridge(alpha=0.1)
    ridge.fit(train_scaled, train_target)
    print(ridge.score(train_scaled, train_target))
    print(ridge.score(test_scaled, test_target))

    # Lasso도 해보기(일부 계수를 0으로 만들어 특성 선택 효과)
    from sklearn.linear_model import Lasso
    lasso = Lasso(alpha=1.0)
    lasso.fit(train_scaled, train_target)
    print(lasso.score(train_scaled, train_target))
    print(lasso.score(test_scaled, test_target))

    train_score, test_score = [], []
    alpha_list = [0.001, 0.01, 0.1, 1, 10, 100]
    for alpha in alpha_list:
        lasso = Lasso(alpha=alpha, max_iter=10000)
        lasso.fit(train_scaled, train_target)
        train_score.append(lasso.score(train_scaled, train_target))
        test_score.append(lasso.score(test_scaled, test_target))
    plt.plot(np.log10(alpha_list), train_score, label='train R^2')
    plt.plot(np.log10(alpha_list), test_score,  label='test R^2')
    plt.xlabel('log10(alpha)'); plt.ylabel('R^2'); plt.legend(); plt.show()

    lasso = Lasso(alpha=10)
    lasso.fit(train_scaled, train_target)
    print(lasso.score(train_scaled, train_target))
    print(lasso.score(test_scaled, test_target))

# -------------------------------
# 7. (보너스) 물고기 분류: 로지스틱/SGD
# -------------------------------
# 여기부터는 "회귀"가 아니라 "분류" 예제입니다.
try:
    import pandas as pd
    fish = pd.read_csv('C:/cv_workspace/data/fish.csv')
    print(pd.unique(fish['Species']))  # 예상 출력: ['Bream' 'Roach' ...] 종류 목록

    fish_input = fish[['Weight','Length','Diagonal','Height','Width']]
    fish_target = fish['Species']

    train_input, test_input, train_target, test_target = train_test_split(
        fish_input, fish_target, random_state=42
    )
    print(train_input.shape)  # 예: (104,5)
    print(test_input.shape)   # 예: (35,5)

    from sklearn.preprocessing import StandardScaler
    ss = StandardScaler()
    ss.fit(train_input)
    train_scaled = ss.transform(train_input)
    test_scaled  = ss.transform(test_input)
    print(train_scaled[:5])   # 표준화된 값 일부 (평균0, 표준편차1 근처)

    # 도미와 빙어만 골라서 이진 분류 해보기
    bream_smelt_indexes = (train_target == 'Bream') | (train_target == 'Smelt')
    train_bream_smelt   = train_scaled[bream_smelt_indexes]
    target_bream_smelt  = train_target[bream_smelt_indexes]
    print(train_bream_smelt.shape)  # 예: (몇십, 5)
    print(target_bream_smelt.shape)

    from sklearn.linear_model import LogisticRegression
    lr = LogisticRegression()
    lr.fit(train_bream_smelt, target_bream_smelt)

    print(lr.predict(train_bream_smelt[:5]))      # 예: ['Bream' 'Smelt' ...]
    print(lr.predict_proba(train_bream_smelt[:5]))# 각 클래스 확률
    print(lr.classes_)                             # 클래스 이름들
    print(lr.coef_.shape, lr.intercept_.shape)     # 가중치, 절편 shape

    # 다중 분류 전체로 학습
    lr = LogisticRegression(C=20, max_iter=1000)
    lr.fit(train_scaled, train_target)
    print(lr.score(train_scaled, train_target))  # 훈련 정확도
    print(lr.score(test_scaled,  test_target))   # 테스트 정확도

    print(lr.predict(test_scaled[:5]))

    proba = lr.predict_proba(test_scaled[:5])
    print(np.round(proba, decimals=3))

    print(lr.coef_.shape, lr.intercept_.shape)

    decision = lr.decision_function(test_scaled[:3])
    print(np.round(decision, decimals=2))

    from scipy.special import softmax
    proba = softmax(decision, axis=1)
    print(np.round(proba, decimals=3))

    # SGDClassifier로 확률적 경사하강법 분류
    from sklearn.linear_model import SGDClassifier
    sc = SGDClassifier(loss='log_loss', max_iter=10, random_state=42)
    sc.fit(train_scaled, train_target)
    print(sc.score(train_scaled, train_target))
    print(sc.score(test_scaled,  test_target))

    sc.partial_fit(train_scaled, train_target)
    print(sc.score(train_scaled, train_target))
    print(sc.score(test_scaled,  test_target))

    sc = SGDClassifier(loss='log_loss', random_state=42)
    train_score, test_score = [], []
    classes = np.unique(train_target)
    for _ in range(0, 300):
        sc.partial_fit(train_scaled, train_target, classes=classes)
        train_score.append(sc.score(train_scaled, train_target))
        test_score.append(sc.score(test_scaled,  test_target))

    plt.plot(train_score); plt.plot(test_score)
    plt.xlabel('epoch'); plt.ylabel('accuracy'); plt.show()

    sc = SGDClassifier(loss='log_loss', max_iter=100, tol=None, random_state=42)
    sc.fit(train_scaled, train_target)
    print(sc.score(train_scaled, train_target))
    print(sc.score(test_scaled,  test_target))

    sc = SGDClassifier(loss='hinge', max_iter=100, tol=None, random_state=42)
    sc.fit(train_scaled, train_target)
    print(sc.score(train_scaled, train_target))
    print(sc.score(test_scaled,  test_target))

except Exception as e:
    print("[참고] fish.csv 등을 찾지 못해 분류 파트 전체를 건너뜁니다.", e)

# -------------------------------
# (끝) 고생 많았어요!
# -------------------------------
