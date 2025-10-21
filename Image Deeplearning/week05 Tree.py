# -*- coding: utf-8 -*-
"""
파일 이름: week05_Tree_annotated.py

무엇을 하나요?
- 의사결정나무(Decision Tree)로 분류를 연습합니다.
- ID3(엔트로피), CART(gini) 시도 + 시각화
- 와인 데이터로 교차검증/그리드서치/랜덤탐색
- 랜덤포레스트/익스트라트리/그라디언트부스팅/HistGB 등 앙상블까지

주의:
- 일부 데이터는 인터넷/로컬에서 불러옵니다. (와인 CSV, 깃허브 CSV)
- 경로가 다르면 본인 PC에 맞게 수정하세요.
"""

import pandas as pd
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn import tree
import matplotlib.pyplot as plt
import numpy as np

# -------------------------------
# 1) 깃허브 CSV(AllElectronics) 불러오기 + 전처리
# -------------------------------
# (Tip) 인터넷 연결 필요. 연결이 안 되면 아래 try/except로 메시지 출력됩니다.
try:
    df = pd.read_csv('https://raw.githubusercontent.com/AugustLONG/ML01/master/01decisiontree/AllElectronics.csv')
    print(df.head())
except Exception as e:
    print("[참고] 깃허브 CSV를 불러오지 못했습니다.", e)
    df = None

if df is not None:
    # 불필요 열 제거(RID)
    df.drop(columns='RID', inplace=True)

    # 범주형 -> 숫자 매핑 (머신러닝이 이해하기 쉬운 숫자로 바꿔줍니다)
    df['age']            = df['age'].map({'youth': 0, 'middle_aged': 1, 'senior': 2})
    df['income']         = df['income'].map({'high': 0, 'medium': 1, 'low': 2})
    df['student']        = df['student'].map({'no': 0, 'yes': 1})
    df['credit_rating']  = df['credit_rating'].map({'fair': 0, 'excellent': 1})
    df['class_buys_computer'] = df['class_buys_computer'].map({"yes": 1, "no": 0})
    print(df.head())  # 매핑 뒤 숫자로 바뀐 모습

    # 입력(X)/정답(y) 분리
    y = df.pop("class_buys_computer")
    X = df
    print(X.shape)  # 예: (14,4)
    print(y.shape)  # 예: (14,)

    # -------------------------------
    # 2) ID3(엔트로피) 트리 학습 + 시각화
    # -------------------------------
    id3 = DecisionTreeClassifier(criterion='entropy', random_state=42)
    id3.fit(X, y)

    plt.figure(figsize=(18, 10))
    plot_tree(id3, feature_names=X.columns, class_names=['no', 'yes'], filled=True, fontsize=12)
    plt.title("ID3 Tree (criterion='entropy')"); plt.show()

    # 새 손님 한 명 예측: [age, income, student, credit_rating] = [0, 1, 1, 0]
    new_data = [[0, 1, 1, 0]]
    prediction = id3.predict(new_data)
    print("구매 예측(ID3):", "yes" if prediction[0] == 1 else "no")  # 예상 출력(예시): yes 또는 no

    # -------------------------------
    # 3) CART(gini) 트리 학습 + 시각화
    # -------------------------------
    cart = DecisionTreeClassifier(criterion="gini", random_state=0)
    cart.fit(X, y)

    plt.figure(figsize=(18, 10))
    tree.plot_tree(cart, feature_names=X.columns, class_names=["not buy", "buy"], filled=True, fontsize=12)
    plt.title("CART Decision Tree (criterion='gini')"); plt.show()

    prediction = cart.predict(new_data)
    print("구매 예측(CART):", "buy" if prediction[0] == 1 else "not buy")

# -------------------------------
# 4) 와인 데이터(로컬 CSV)로 다양한 실험
# -------------------------------
try:
    wine = pd.read_csv('C:/cv_workspace/data/wine.csv')
    print(wine.head(3)); print(wine.info())
except Exception as e:
    print("[참고] wine.csv 를 불러오지 못했습니다.", e)
    wine = None

if wine is not None:
    data   = wine[['alcohol', 'sugar', 'pH']]
    target = wine['class']

    from sklearn.model_selection import train_test_split
    train_input, test_input, train_target, test_target = train_test_split(
        data, target, test_size=0.2, random_state=42
    )
    print(train_input.shape, test_input.shape)

    # 표준화(스케일 조정)
    from sklearn.preprocessing import StandardScaler
    ss = StandardScaler()
    ss.fit(train_input)
    train_scaled = ss.transform(train_input)
    test_scaled  = ss.transform(test_input)
    print(train_scaled[:3])

    # 기본 트리
    dt = DecisionTreeClassifier(random_state=42)
    dt.fit(train_scaled, train_target)
    print(dt.score(train_scaled, train_target))  # 훈련 정확도
    print(dt.score(test_scaled,  test_target))   # 테스트 정확도

    # 깊이 제한: 과적합 줄이기
    dt = DecisionTreeClassifier(max_depth=3, random_state=42)
    dt.fit(train_scaled, train_target)
    print(dt.score(train_scaled, train_target))
    print(dt.score(test_scaled,  test_target))

    plt.figure(figsize=(20,15))
    plot_tree(dt, filled=True, feature_names=['alcohol', 'sugar', 'pH'])
    plt.title('Depth=3 Tree'); plt.show()

    print(dt.feature_importances_)  # 어떤 특성이 중요한가? (예: sugar 비중이 큼)

    # -------------------------------
    # 5) 검증법: 홀드아웃/교차검증/StratifiedKFold
    # -------------------------------
    sub_input, val_input, sub_target, val_target = train_test_split(
        train_input, train_target, test_size=0.2, random_state=42
    )
    dt = DecisionTreeClassifier(random_state=42)
    dt.fit(sub_input, sub_target)
    print(dt.score(sub_input, sub_target))  # 학습 부분 정확도
    print(dt.score(val_input, val_target))  # 검증 부분 정확도

    from sklearn.model_selection import cross_validate, StratifiedKFold, GridSearchCV
    scores = cross_validate(dt, train_input, train_target)
    print(scores)
    print(np.mean(scores['test_score']))

    scores = cross_validate(dt, train_input, train_target, cv=StratifiedKFold())
    print(np.mean(scores['test_score']))

    splitter = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
    scores = cross_validate(dt, train_input, train_target, cv=splitter)
    print(np.mean(scores['test_score']))

    # -------------------------------
    # 6) 하이퍼파라미터 최적화: GridSearch / RandomizedSearch
    # -------------------------------
    params = {'min_impurity_decrease': [0.0001, 0.0002, 0.0003, 0.0004, 0.0005]}
    gs = GridSearchCV(DecisionTreeClassifier(random_state=42), params, n_jobs=-1)
    gs.fit(train_input, train_target)
    dt = gs.best_estimator_
    print(dt.score(train_input, train_target))
    print(gs.best_params_)
    print(gs.cv_results_['mean_test_score'])
    print(gs.cv_results_['params'][gs.best_index_])

    params = {
        'min_impurity_decrease': np.arange(0.0001, 0.001, 0.0001),
        'max_depth': range(5, 20, 1),
        'min_samples_split': range(2, 100, 10)
    }
    gs = GridSearchCV(DecisionTreeClassifier(random_state=42), params, n_jobs=-1)
    gs.fit(train_input, train_target)
    print(gs.best_params_)
    print(np.max(gs.cv_results_['mean_test_score']))

    from scipy.stats import uniform, randint
    rgen = randint(0, 10)
    print(rgen.rvs(10))                     # 무작위 정수 예시
    print(np.unique(rgen.rvs(1000), return_counts=True))
    ugen = uniform(0, 1)
    print(ugen.rvs(10))                     # 무작위 실수 예시

    params = {
        'min_impurity_decrease': uniform(0.0001, 0.001),
        'max_depth': randint(20, 50),
        'min_samples_split': randint(2, 25),
        'min_samples_leaf' : randint(1, 25),
    }
    from sklearn.model_selection import RandomizedSearchCV
    rs = RandomizedSearchCV(DecisionTreeClassifier(random_state=42), params,
                            n_iter=100, n_jobs=-1, random_state=42)
    rs.fit(train_input, train_target)
    print(rs.best_params_)

    # -------------------------------
    # 7) 앙상블 학습: RF/ExtraTrees/GB/HistGB
    # -------------------------------
    from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier, HistGradientBoostingClassifier

    rf = RandomForestClassifier(n_jobs=-1, random_state=42)
    scores = cross_validate(rf, train_input, train_target, return_train_score=True, n_jobs=-1)
    print(np.mean(scores['train_score']), np.mean(scores['test_score']))

    rf = RandomForestClassifier(oob_score=True, n_jobs=-1, random_state=42)
    rf.fit(train_input, train_target)
    print(rf.oob_score_)

    et = ExtraTreesClassifier(n_jobs=-1, random_state=42)
    scores = cross_validate(et, train_input, train_target, return_train_score=True, n_jobs=-1)
    print(np.mean(scores['train_score']), np.mean(scores['test_score']))

    et.fit(train_input, train_target)
    print(et.feature_importances_)  # 특성중요도

    gb = GradientBoostingClassifier(random_state=42)
    scores = cross_validate(gb, train_input, train_target, return_train_score=True, n_jobs=-1)
    print(np.mean(scores['train_score']), np.mean(scores['test_score']))

    gb = GradientBoostingClassifier(n_estimators=500, learning_rate=0.2, random_state=42)
    scores = cross_validate(gb, train_input, train_target, return_train_score=True, n_jobs=-1)
    print(np.mean(scores['train_score']), np.mean(scores['test_score']))

    gb.fit(train_input, train_target)
    print(gb.feature_importances_)

    hgb = HistGradientBoostingClassifier(random_state=42)
    scores = cross_validate(hgb, train_input, train_target, return_train_score=True)
    print(np.mean(scores['train_score']), np.mean(scores['test_score']))

    from sklearn.inspection import permutation_importance
    hgb.fit(train_input, train_target)
    result = permutation_importance(hgb, train_input, train_target, n_repeats=10, random_state=42, n_jobs=-1)
    print(result.importances_mean)

    result = permutation_importance(hgb, test_input, test_target, n_repeats=10, random_state=42, n_jobs=-1)
    print(result.importances_mean)

    print(hgb.score(test_input, test_target))

# 끝!
