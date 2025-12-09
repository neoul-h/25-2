#week09 image process II
import cv2 as cv
import numpy as np

img=cv.imread('C:/cv_workspace/data/soccer.jpg')
img=cv.resize(img,dsize=(0,0),fx=0.25,fy=0.25)

def gamma(f,gamma=1.0):
    f1=f/255.0# L=256이라고 가정
    return np.uint8(255*(f1**gamma))

gc=np.hstack((gamma(img,0.5),gamma(img,0.75),gamma(img,1.0),gamma(img,2.0),gamma(img,3.0)))
cv.imshow('gamma',gc)

cv.waitKey()
cv.destroyAllWindows()


img=cv.imread('C:/cv_workspace/data/soccer.jpg')
img=cv.resize(img,dsize=(0,0),fx=0.4,fy=0.4)
gray=cv.cvtColor(img,cv.COLOR_BGR2GRAY)
cv.putText(gray,'soccer',(10,20),cv.FONT_HERSHEY_SIMPLEX,0.7,(255,255,255),2)
cv.imshow('Original',gray)

smooth=np.hstack((cv.GaussianBlur(gray,(5,5),0.0),cv.GaussianBlur(gray,(9,9),0.0),cv.GaussianBlur(gray,(15,15),0.0)))
cv.imshow('Smooth',smooth)

femboss=np.array([[-1.0, 0.0, 0.0],
                  [ 0.0, 0.0, 0.0],
                  [ 0.0, 0.0, 1.0]])

gray16=np.int16(gray)
emboss=np.uint8(np.clip(cv.filter2D(gray16,-1,femboss)+128,0,255))
emboss_bad=np.uint8(cv.filter2D(gray16,-1,femboss)+128)
emboss_worse=cv.filter2D(gray,-1,femboss)

cv.imshow('Emboss',emboss)
cv.imshow('Emboss_bad',emboss_bad)
cv.imshow('Emboss_worse',emboss_worse)

cv.waitKey()
cv.destroyAllWindows()


img=cv.imread('C:/cv_workspace/data/rose.png')
patch=img[250:350,170:270,:]

img=cv.rectangle(img,(170,250),(270,350),(255,0,0),3)
patch1=cv.resize(patch,dsize=(0,0),fx=5,fy=5,interpolation=cv.INTER_NEAREST)
patch2=cv.resize(patch,dsize=(0,0),fx=5,fy=5,interpolation=cv.INTER_LINEAR)
patch3=cv.resize(patch,dsize=(0,0),fx=5,fy=5,interpolation=cv.INTER_CUBIC)

cv.imshow('Original',img)
cv.imshow('Resize nearest',patch1) 
cv.imshow('Resize bilinear',patch2) 
cv.imshow('Resize bicubic',patch3) 

cv.waitKey()
cv.destroyAllWindows()

#week10 edge and area split
import cv2 as cv

img=cv.imread('C:/cv_workspace/data/soccer.jpg')
gray=cv.cvtColor(img,cv.COLOR_BGR2GRAY)

grad_x=cv.Sobel(gray,cv.CV_32F,1,0,ksize=3) ## 소벨 연산자 적용
grad_y=cv.Sobel(gray,cv.CV_32F,0,1,ksize=3)

sobel_x=cv.convertScaleAbs(grad_x)# 절대값을 취해 양수 영상으로 변환
sobel_y=cv.convertScaleAbs(grad_y)

edge_strength=cv.addWeighted(sobel_x,0.5,sobel_y,0.5,0)# 에지 강도 계산

cv.imshow('Original',gray)
cv.imshow('sobelx',sobel_x)
cv.imshow('sobely',sobel_y)
cv.imshow('edge strength',edge_strength)

cv.waitKey()
cv.destroyAllWindows()


img=cv.imread('C:/cv_workspace/data/soccer.jpg')

gray=cv.cvtColor(img,cv.COLOR_BGR2GRAY)

canny1=cv.Canny(gray,50,150)# Tlow=50, Thigh=150으로 설정
canny2=cv.Canny(gray,100,200)# Tlow=100, Thigh=200으로 설정

cv.imshow('Original',gray)
cv.imshow('Canny1',canny1)
cv.imshow('Canny2',canny2)

cv.waitKey()
cv.destroyAllWindows()


img=cv.imread('C:/cv_workspace/data/soccer.jpg')
gray=cv.cvtColor(img,cv.COLOR_BGR2GRAY)
canny=cv.Canny(gray,100,200) 

contour,hierarchy=cv.findContours(canny,cv.RETR_LIST,cv.CHAIN_APPROX_NONE)

lcontour=[]   
for i in range(len(contour)):
    if contour[i].shape[0]>100:# 길이가 100보다 크면
        lcontour.append(contour[i])

cv.drawContours(img,lcontour,-1,(0,255,0),3)
            
cv.imshow('Original with contours',img)    
cv.imshow('Canny',canny)    

cv.waitKey()
cv.destroyAllWindows()



img=cv.imread('C:/cv_workspace/data/apples.jpg')
gray=cv.cvtColor(img,cv.COLOR_BGR2GRAY)

apples=cv.HoughCircles(gray,cv.HOUGH_GRADIENT,1,200,param1=150,param2=20,minRadius=50,maxRadius=120)

for i in apples[0]: 
    cv.circle(img,(int(i[0]),int(i[1])),int(i[2]),(255,0,0),2)

cv.imshow('Apple detection',img)  

cv.waitKey()
cv.destroyAllWindows()


import skimage
import numpy as np
import cv2 as cv

img=skimage.data.coffee()
cv.imshow('Coffee image',cv.cvtColor(img,cv.COLOR_RGB2BGR))

slic1=skimage.segmentation.slic(img,compactness=20,n_segments=600)
sp_img1=skimage.segmentation.mark_boundaries(img,slic1)
sp_img1=np.uint8(sp_img1*255.0)

slic2=skimage.segmentation.slic(img,compactness=40,n_segments=600)
sp_img2=skimage.segmentation.mark_boundaries(img,slic2)
sp_img2=np.uint8(sp_img2*255.0)

cv.imshow('Super pixels (compact 20)',cv.cvtColor(sp_img1,cv.COLOR_RGB2BGR))
cv.imshow('Super pixels (compact 40)',cv.cvtColor(sp_img2,cv.COLOR_RGB2BGR))

cv.waitKey()
cv.destroyAllWindows()


""" colab 버젼
import skimage
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
img=skimage.data.coffee()

slic1=skimage.segmentation.slic(img,compactness=20,n_segments=600)
sp_img1=skimage.segmentation.mark_boundaries(img,slic1)
sp_img1=np.uint8(sp_img1*255.0)

slic2=skimage.segmentation.slic(img,compactness=40,n_segments=600)
sp_img2=skimage.segmentation.mark_boundaries(img,slic2)
sp_img2=np.uint8(sp_img2*255.0)

plt.figure(figsize=(15, 5))
plt.subplot(1, 3, 1)
plt.imshow(cv.cvtColor(img,cv.COLOR_RGB2BGR))
plt.title('Coffee image')
plt.axis('off')

plt.subplot(1, 3, 2)
plt.imshow(cv.cvtColor(sp_img1, cv.COLOR_BGR2RGB))
plt.title('Super pixels (compact 20)')
plt.axis('off')

plt.subplot(1, 3, 3)
plt.imshow(cv.cvtColor(sp_img2, cv.COLOR_BGR2RGB))
plt.title('Super pixels (compact 40)')
plt.axis('off')

plt.tight_layout()
plt.show()

"""


import skimage
from skimage import graph
from skimage import segmentation
import numpy as np
import cv2 as cv
import time

coffee=skimage.data.coffee()

start=time.time()#처리 시작

slic = segmentation.slic(coffee, compactness=30, n_segments=600)
g = graph.rag_mean_color(coffee, slic, mode='similarity')

ncut=graph.cut_normalized(slic,g)# 정규화 절단
print(coffee.shape,' Coffee 영상을 분할하는데 ',time.time()-start,'초 소요')

marking=skimage.segmentation.mark_boundaries(coffee,ncut)
ncut_coffee=np.uint8(marking*255.0)

cv.imshow('Normalized cut',cv.cvtColor(ncut_coffee,cv.COLOR_RGB2BGR))  

cv.waitKey()
cv.destroyAllWindows()


"""colab 버젼
import skimage
from skimage import graph
from skimage import segmentation
import numpy as np
import cv2 as cv
import time
import matplotlib.pyplot as plt

coffee=skimage.data.coffee()

start=time.time()#처리 시작

slic = segmentation.slic(coffee, compactness=30, n_segments=600)
g = graph.rag_mean_color(coffee, slic, mode='similarity')

ncut=graph.cut_normalized(slic,g)# 정규화 절단
print(coffee.shape,' Coffee 영상을 분할하는데 ',time.time()-start,'초 소요')

marking=skimage.segmentation.mark_boundaries(coffee,ncut)
ncut_coffee=np.uint8(marking*255.0)

plt.imshow(cv.cvtColor(ncut_coffee, cv.COLOR_BGR2RGB))
plt.title('Normalized cut')
plt.axis('off')
plt.show()

"""


import skimage
import numpy as np
import cv2 as cv

# skimage에서 말(horse) 이진 영상 불러오기
orig = skimage.data.horse()

# 말 영상은 흰색(1) 부분이 객체이므로, 이를 반전하여 흑색 객체로 변환
# np.uint8로 변환 후 255를 곱해 픽셀값을 0~255 범위로 확장
img = 255 - np.uint8(orig) * 255
cv.imshow('Horse', img)

# 외곽선(contour) 검출
# RETR_EXTERNAL: 외곽선 중 가장 바깥쪽만 검출
# CHAIN_APPROX_NONE: 외곽선의 모든 점을 저장 (압축 없음)
contours, hierarchy = cv.findContours(img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

# 컬러 영상으로 변환 (외곽선 표시용)
img2 = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
# 모든 외곽선을 자홍색(보라색, (255,0,255))으로 두께 2로 그림
cv.drawContours(img2, contours, -1, (255, 0, 255), 2)
cv.imshow('Horse with contour', img2)

# 첫 번째 외곽선 선택 (하나의 말 외곽선)
contour = contours[0]

# 모멘트 계산 (면적, 중심좌표 등 기하학적 특징 추출)
m = cv.moments(contour)
area = cv.contourArea(contour)  # 면적
cx, cy = m['m10'] / m['m00'], m['m01'] / m['m00']  # 무게중심 좌표
perimeter = cv.arcLength(contour, True)  # 둘레 길이
roundness = (4.0 * np.pi * area) / (perimeter * perimeter)  # 둥근 정도 (1에 가까울수록 원형)
print('면적 =', area, '\n중점 = (', cx, ',', cy, ')',
      '\n둘레 =', perimeter, '\n둥근 정도 =', roundness)

# 컬러 영상 복제 (직선 근사, 볼록헐 표시용)
img3 = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
# 외곽선의 직선 근사 (epsilon=8 픽셀 오차 허용)
contour_approx = cv.approxPolyDP(contour, 8, True)
# 근사된 외곽선을 녹색(0,255,0)으로 표시
cv.drawContours(img3, [contour_approx], -1, (0, 255, 0), 2)
# 볼록 헐(Convex Hull) 계산 — 가장 바깥쪽 꼭짓점을 연결한 다각형
hull = cv.convexHull(contour)
# 그리기 위해 (1, N, 2) 형태로 reshape
hull = hull.reshape(1, hull.shape[0], hull.shape[2])
# 볼록 헐을 빨간색(0,0,255)으로 표시
cv.drawContours(img3, hull, -1, (0, 0, 255), 2)

# 직선 근사선과 볼록 헐을 함께 표시한 결과 출력
cv.imshow('Horse with line segments and convex hull', img3)


cv.waitKey()
cv.destroyAllWindows()


"""colab 버전
import skimage
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
plt.figure(figsize=(15, 5))
plt.subplot(1, 3, 1)
orig=skimage.data.horse()
img=255-np.uint8(orig)*255
plt.axis('off')
plt.title('Horse')
plt.imshow(img)

contours,hierarchy=cv.findContours(img,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_NONE)

img2=cv.cvtColor(img,cv.COLOR_GRAY2BGR)# 컬러 디스플레이용 영상
cv.drawContours(img2,contours,-1,(255,0,255),2)
plt.subplot(1, 3, 2)
plt.axis('off')
plt.title('Horse with contour')
plt.imshow(img2)

contour=contours[0]

m=cv.moments(contour)# 몇 가지 특징 
area=cv.contourArea(contour)
cx,cy=m['m10']/m['m00'],m['m01']/m['m00']
perimeter=cv.arcLength(contour,True)
roundness=(4.0*np.pi*area)/(perimeter*perimeter)
print('면적=',area,'\n중점=(',cx,',',cy,')','\n둘레=',perimeter,'\n둥근 정도=',roundness)

img3=cv.cvtColor(img,cv.COLOR_GRAY2BGR)# 컬러 디스플레이용 영상

contour_approx=cv.approxPolyDP(contour,8,True)# 직선 근사
cv.drawContours(img3,[contour_approx],-1,(0,255,0),2)

hull=cv.convexHull(contour)# 볼록 헐
hull=hull.reshape(1,hull.shape[0],hull.shape[2])
cv.drawContours(img3,hull,-1,(0,0,255),2)

plt.subplot(1, 3, 3)
plt.imshow(img3)
plt.title('Horse with line segments and convex hull')
plt.axis('off')
plt.tight_layout()
plt.show()

"""


#week11 Artificial Neural Network
import numpy as np
import tensorflow as tf
import tensorflow.keras.datasets as ds

from tensorflow.keras.models import Sequential

from tensorflow.keras.layers import Dense

from tensorflow.keras.optimizers import SGD

from tensorflow.keras.optimizers import Adam



(x_train,y_train),(x_test,y_test)=ds.mnist.load_data()

x_train=x_train.reshape(60000,784)

x_test=x_test.reshape(10000,784)

x_train=x_train.astype(np.float32)/255.0

x_test=x_test.astype(np.float32)/255.0

y_train=tf.keras.utils.to_categorical(y_train,10)

y_test=tf.keras.utils.to_categorical(y_test,10)



mlp=Sequential()

mlp.add(Dense(units=512,activation='tanh',input_shape=(784,)))

mlp.add(Dense(units=10,activation='softmax'))



#경사하강법

mlp.compile(loss='MSE',optimizer=SGD(learning_rate=0.01),metrics=['accuracy'])

#최적화

#mlp.compile(loss='MSE',optimizer=Adam(learning_rate=0.001),metrics=['accuracy'])

mlp.fit(x_train,y_train,batch_size=128,epochs=50,validation_data=(x_test,y_test),verbose=2)



res=mlp.evaluate(x_test,y_test,verbose=0)



print('정확률=',res[1]*100)





import cv2

img = cv2.imread('C:/cv_workspace/data/number.png', cv2.IMREAD_GRAYSCALE)



img = cv2.resize(img, (28, 28)) # 28x28로 리사이즈

img = img / 255.0# 0~1 정규화



x_input = img.reshape(1, 784)# (1, 784) 형태로 reshape



# 예측

pred = mlp.predict(x_input)

predicted_label = np.argmax(pred)

print("예측된 숫자:", predicted_label)







import numpy as np

import tensorflow as tf

import tensorflow.keras.datasets as ds



from tensorflow.keras.models import Sequential

from tensorflow.keras.layers import Dense

from tensorflow.keras.optimizers import SGD, Adam



(x_train,y_train),(x_test,y_test)=ds.mnist.load_data()

x_train=x_train.reshape(60000,784)

x_test=x_test.reshape(10000,784)

x_train=x_train.astype(np.float32)/255.0

x_test=x_test.astype(np.float32)/255.0

y_train=tf.keras.utils.to_categorical(y_train,10)

y_test=tf.keras.utils.to_categorical(y_test,10)



mlp_sgd=Sequential()

mlp_sgd.add(Dense(units=512,activation='tanh',input_shape=(784,)))

mlp_sgd.add(Dense(units=10,activation='softmax'))



mlp_sgd.compile(loss='MSE',optimizer=SGD(learning_rate=0.01),metrics=['accuracy'])

hist_sgd=mlp_sgd.fit(x_train,y_train,batch_size=128,epochs=50,validation_data=(x_test,y_test),verbose=2)

print('SGD 정확률=',mlp_sgd.evaluate(x_test,y_test,verbose=0)[1]*100)



mlp_adam=Sequential()

mlp_adam.add(Dense(units=512,activation='tanh',input_shape=(784,)))

mlp_adam.add(Dense(units=10,activation='softmax'))



mlp_adam.compile(loss='MSE',optimizer=Adam(learning_rate=0.001),metrics=['accuracy'])

hist_adam=mlp_adam.fit(x_train,y_train,batch_size=128,epochs=50,validation_data=(x_test,y_test),verbose=2)

print('Adam 정확률=',mlp_adam.evaluate(x_test,y_test,verbose=0)[1]*100)



import matplotlib.pyplot as plt



plt.plot(hist_sgd.history['accuracy'],'r--')

plt.plot(hist_sgd.history['val_accuracy'],'r')

plt.plot(hist_adam.history['accuracy'],'b--')

plt.plot(hist_adam.history['val_accuracy'],'b')

plt.title('Comparison of SGD and Adam optimizers')

plt.ylim((0.7,1.0))

plt.xlabel('epochs')

plt.ylabel('accuracy')

plt.legend(['train_sgd','val_sgd','train_adam','val_adam'])

plt.grid()

plt.show()





import numpy as np

import tensorflow as tf

import tensorflow.keras.datasets as ds



from tensorflow.keras.models import Sequential

from tensorflow.keras.layers import Dense

from tensorflow.keras.optimizers import Adam



(x_train,y_train),(x_test,y_test)=ds.mnist.load_data()

x_train=x_train.reshape(60000,784)

x_test=x_test.reshape(10000,784)

x_train=x_train.astype(np.float32)/255.0

x_test=x_test.astype(np.float32)/255.0

y_train=tf.keras.utils.to_categorical(y_train,10)

y_test=tf.keras.utils.to_categorical(y_test,10)



dmlp=Sequential()

dmlp.add(Dense(units=1024,activation='relu',input_shape=(784,)))

dmlp.add(Dense(units=512,activation='relu'))

dmlp.add(Dense(units=512,activation='relu'))

dmlp.add(Dense(units=10,activation='softmax'))



dmlp.compile(loss='categorical_crossentropy',optimizer=Adam(learning_rate=0.0001),metrics=['accuracy'])

hist=dmlp.fit(x_train,y_train,batch_size=128,epochs=50,validation_data=(x_test,y_test),verbose=2)

print('정확률=', dmlp.evaluate(x_test,y_test,verbose=0)[1]*100)



dmlp.save('dmlp_trained.h5')



import matplotlib.pyplot as plt



plt.plot(hist.history['accuracy'])

plt.plot(hist.history['val_accuracy'])

plt.title('Accuracy graph')

plt.xlabel('epochs')

plt.ylabel('accuracy')

plt.legend(['train','test'])

plt.grid()

plt.show()



plt.plot(hist.history['loss'])

plt.plot(hist.history['val_loss'])

plt.title('Loss graph')

plt.xlabel('epochs')

plt.ylabel('loss')

plt.legend(['train','test'])

plt.grid()

plt.show()







import cv2

img = cv2.imread('C:/cv_workspace/data/number.png', cv2.IMREAD_GRAYSCALE)



img = cv2.resize(img, (28, 28)) # 28x28로 리사이즈

img = img / 255.0# 0~1 정규화



x_input = img.reshape(1, 784)# (1, 784) 형태로 reshape



# 예측

pred = dmlp.predict(x_input)

predicted_label = np.argmax(pred)

print("예측된 숫자:", predicted_label)

#week12_Convolutional Neural Network(CNN)I
import keras

keras.layers.Conv2D(10, kernel_size=(3, 3), activation='relu')



keras.layers.Conv2D(10, kernel_size=(3,3), activation='relu', padding='same')



keras.layers.Conv2D(10, kernel_size=(3,3), activation='relu', padding='same', strides=1)



keras.layers.MaxPooling2D(2)



keras.layers.MaxPooling2D(2, strides=2, padding='valid')



import keras

from sklearn.model_selection import train_test_split



#데이터 로드

(train_input, train_target), (test_input, test_target) =keras.datasets.fashion_mnist.load_data()



# MNIST 이미지 데이터를 CNN 입력 형식에 맞게 변환

# -1: 전체 이미지 개수 자동 계산

# 28, 28: MNIST 원본 이미지 크기(28x28 픽셀)

# 1: 흑백 이미지 채널 수

# /255.0: 픽셀 값을 0~255 → 0~1 범위로 정규화

train_scaled = train_input.reshape(-1, 28, 28, 1) / 255.0



train_scaled, val_scaled, train_target, val_target = train_test_split(

     train_scaled, train_target, test_size=0.2, random_state=42)



model = keras.Sequential()

model.add(keras.layers.Input(shape=(28,28,1)))

model.add(keras.layers.Conv2D(32, kernel_size=3, activation='relu', padding='same'))



model.add(keras.layers.MaxPooling2D(2))



model.add(keras.layers.Conv2D(64, kernel_size=3, activation='relu', padding='same'))

model.add(keras.layers.MaxPooling2D(2))



model.add(keras.layers.Flatten())

model.add(keras.layers.Dense(100, activation='relu'))

model.add(keras.layers.Dropout(0.4))

model.add(keras.layers.Dense(10, activation='softmax'))





model.summary()



# 모델 컴파일: 

# - optimizer='adam' : Adam 최적화 알고리즘 사용

# - loss='sparse_categorical_crossentropy' : 정답 라벨이 정수(0~9)인 경우 사용하는 다중분류 손실 함수

# - metrics=['accuracy'] : 정확도를 평가 지표로 사용

model.compile(optimizer='adam', 

              loss='sparse_categorical_crossentropy', 

              metrics=['accuracy'])



# 체크포인트 콜백:

# - save_best_only=True : 검증 손실이 가장 낮을 때의 가중치만 저장

checkpoint_cb = keras.callbacks.ModelCheckpoint(

    'best-cnn-model.keras', save_best_only=True)



# 조기 종료 콜백:

# - patience=2 : 검증 성능이 2 epoch 동안 개선되지 않으면 학습 중단

# - restore_best_weights=True : 가장 좋은 가중치로 모델 복원

early_stopping_cb = keras.callbacks.EarlyStopping(

    patience=2, restore_best_weights=True)



# 모델 학습:

# - epochs=20 : 최대 20 epoch 학습

# - validation_data : 검증 데이터 제공

# - callbacks : 체크포인트와 조기 종료 기능 적용

history = model.fit(train_scaled, train_target, epochs=20,

                    validation_data=(val_scaled, val_target),

                    callbacks=[checkpoint_cb, early_stopping_cb])





import matplotlib.pyplot as plt



plt.plot(history.history['loss'], label='train')

plt.plot(history.history['val_loss'], label='val')

plt.xlabel('epoch')

plt.ylabel('loss')

plt.legend()

plt.show()



model.evaluate(val_scaled, val_target)



preds = model.predict(val_scaled[0:1])

print(preds)



plt.bar(range(1, 11), preds[0])

plt.xlabel('class')

plt.ylabel('prob.')

plt.show()



classes = ['티셔츠', '바지', '스웨터', '드레스', '코트', '샌달', '셔츠', '스니커즈', '가방', '앵클 부츠']



import numpy as np



print(classes[np.argmax(preds)])



test_scaled = test_input.reshape(-1, 28, 28, 1) / 255.0

ev = model.evaluate(test_scaled, test_target)

print("loss:",ev[0])

print("accuracy:",ev[1])







conv = model.layers[0]

print(conv.weights[0].shape, conv.weights[1].shape)



conv_weights = conv.weights[0].numpy()

print(conv_weights.mean(), conv_weights.std())



import matplotlib.pyplot as plt



plt.hist(conv_weights.reshape(-1, 1))

plt.xlabel('weight')

plt.ylabel('count')

plt.show()



fig, axs = plt.subplots(2, 16, figsize=(15,2))

for i in range(2):

     for j in range(16):

          axs[i, j].imshow(conv_weights[:,:,0,i*16 + j], vmin=-0.5, vmax=0.5)

          axs[i, j].axis('off')

plt.show()



no_training_model = keras.Sequential()

no_training_model.add(keras.layers.Input(shape=(28,28,1)))

no_training_model.add(keras.layers.Conv2D(32, kernel_size=3, activation='relu', padding='same'))



no_training_conv = no_training_model.layers[0]

print(no_training_conv.weights[0].shape)



no_training_weights = no_training_conv.weights[0].numpy()

print(no_training_weights.mean(), no_training_weights.std())



plt.hist(no_training_weights.reshape(-1, 1))

plt.xlabel('weight')

plt.ylabel('count')

plt.show()



fig, axs = plt.subplots(2, 16, figsize=(15,2))

for i in range(2):

    for j in range(16):

        axs[i, j].imshow(no_training_weights[:,:,0,i*16 + j], vmin=-0.5, vmax=0.5)

        axs[i, j].axis('off')

plt.show()



inputs = keras.Input(shape=(784,))

dense1 = keras.layers.Dense(100, activation='relu')

dense2 = keras.layers.Dense(10, activation='softmax')



hidden = dense1(inputs)



outputs = dense2(hidden)



func_model = keras.Model(inputs, outputs)



inputs = keras.Input(shape=(784,))



print(model.inputs)



conv_acti = keras.Model(model.inputs, model.layers[0].output)



(train_input, train_target), (test_input, test_target) = keras.datasets.fashion_mnist.load_data()

plt.imshow(train_input[0], cmap='gray_r')

plt.show()



ankle_boot = train_input[0:1].reshape(-1, 28, 28, 1) / 255.0

feature_maps = conv_acti.predict(ankle_boot)



print(feature_maps.shape)



fig, axs = plt.subplots(4, 8, figsize=(15,8))

for i in range(4):

    for j in range(8):

         axs[i, j].imshow(feature_maps[0,:,:,i*8 + j])

         axs[i, j].axis('off')

plt.show()



conv2_acti = keras.Model(model.inputs, model.layers[2].output)



feature_maps = conv2_acti.predict(ankle_boot)



print(feature_maps.shape)



fig, axs = plt.subplots(8, 8, figsize=(12,12))

for i in range(8):

    for j in range(8):

          axs[i, j].imshow(feature_maps[0,:,:,i*8 + j])

          axs[i, j].axis('off')

plt.show()

#week13_Convolutional Neural Network(CNN)II
import numpy as np

import tensorflow as tf

import tensorflow.keras.datasets as ds



from tensorflow.keras.models import Sequential

from tensorflow.keras.layers import Conv2D,MaxPooling2D,Flatten,Dropout,Dense

from tensorflow.keras.optimizers import Adam



(x_train,y_train),(x_test,y_test)=ds.mnist.load_data()

x_train=x_train.reshape(60000,28,28,1)

x_test=x_test.reshape(10000,28,28,1)

x_train=x_train.astype(np.float32)/255.0

x_test=x_test.astype(np.float32)/255.0

y_train=tf.keras.utils.to_categorical(y_train,10)

y_test=tf.keras.utils.to_categorical(y_test,10)



cnn=Sequential()

cnn.add(Conv2D(6,(5,5),padding='same',activation='relu',input_shape=(28,28,1)))

cnn.add(MaxPooling2D(pool_size=(2,2),strides=2))

cnn.add(Conv2D(16,(5,5),padding='valid',activation='relu'))

cnn.add(MaxPooling2D(pool_size=(2,2),strides=2))

cnn.add(Conv2D(120,(5,5),padding='valid',activation='relu'))

cnn.add(Flatten())

cnn.add(Dense(units=84,activation='relu'))

cnn.add(Dense(units=10,activation='softmax'))



cnn.compile(loss='categorical_crossentropy',optimizer=Adam(learning_rate=0.001),metrics=['accuracy']) 

cnn.fit(x_train,y_train,batch_size=128,epochs=30,validation_data=(x_test,y_test),verbose=2)

                                    

res=cnn.evaluate(x_test,y_test,verbose=0) 

print('정확률=',res[1]*100)





import tensorflow.keras.datasets as ds

from tensorflow.keras.preprocessing.image import ImageDataGenerator

import matplotlib.pyplot as plt



(x_train,y_train),(x_test,y_test)=ds.cifar10.load_data()

x_train=x_train.astype('float32'); x_train/=255

x_train=x_train[0:15,]; y_train=y_train[0:15,]# 앞 15개에 대해서만 증대 적용

class_names=['airplane','automobile','bird','cat','deer','dog','flog','horse','ship','truck']



plt.figure(figsize=(20,2))

plt.suptitle("First 15 images in the train set")

for i in range(15):

    plt.subplot(1,15,i+1)

    plt.imshow(x_train[i])

    plt.xticks([]); plt.yticks([])

    plt.title(class_names[int(y_train[i])])

plt.show()    



batch_siz=4# 한 번에 생성하는 양(미니 배치)

generator=ImageDataGenerator(rotation_range=20.0,width_shift_range=0.2,height_shift_range=0.2,horizontal_flip=True)

gen=generator.flow(x_train,y_train,batch_size=batch_siz)



for a in range(3):

    img,label=next(gen)# 미니 배치만큼 생성, 안되면 gen.next()

    plt.figure(figsize=(8,2.4))

    plt.suptitle("Generatior trial "+str(a+1))

    for i in range(batch_siz):

        plt.subplot(1,batch_siz,i+1)

        plt.imshow(img[i])

        plt.xticks([]); plt.yticks([])

        plt.title(class_names[int(label[i])])

    plt.show()

    

import cv2 as cv 

import numpy as np

from tensorflow.keras.applications.resnet50 import ResNet50,preprocess_input,decode_predictions



model=ResNet50(weights='imagenet')



img=cv.imread('C:/cv_workspace/data/rabbit.jpg')

 

x=np.reshape(cv.resize(img,(224,224)),(1,224,224,3))   

x=preprocess_input(x)



preds=model.predict(x)

top5=decode_predictions(preds,top=5)[0]

print('예측 결과:',top5)



for i in range(5):

    cv.putText(img,top5[i][1]+':'+str(top5[i][2]),(10,20+i*20),cv.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),1)



cv.imshow('Recognition result',img)



cv.waitKey()

cv.destroyAllWindows()

#week14 Yolo.py
import numpy as np
import cv2 as cv
import sys
path = 'C:/cv_workspace/data/'
def construct_yolo_v3():
    f=open(path+'coco_names.txt', 'r')
    class_names=[line.strip() for line in f.readlines()]

    model=cv.dnn.readNet(path+'yolov3.weights',path+'yolov3.cfg')
    layer_names=model.getLayerNames()
    out_layers=[layer_names[i-1] for i in model.getUnconnectedOutLayers()]
    
    return model,out_layers,class_names

def yolo_detect(img,yolo_model,out_layers):
    height,width=img.shape[0],img.shape[1]
    test_img=cv.dnn.blobFromImage(img,1.0/256,(448,448),(0,0,0),swapRB=True)
    
    yolo_model.setInput(test_img)
    output3=yolo_model.forward(out_layers)
    
    box,conf,id=[],[],[]		# 박스, 신뢰도, 부류 번호
    for output in output3:
        for vec85 in output:
            scores=vec85[5:]
            class_id=np.argmax(scores)
            confidence=scores[class_id]
            if confidence>0.5:	# 신뢰도가 50% 이상인 경우만 취함
                centerx,centery=int(vec85[0]*width),int(vec85[1]*height)
                w,h=int(vec85[2]*width),int(vec85[3]*height)
                x,y=int(centerx-w/2),int(centery-h/2)
                box.append([x,y,x+w,y+h])
                conf.append(float(confidence))
                id.append(class_id)
            
    ind=cv.dnn.NMSBoxes(box,conf,0.5,0.4)
    objects=[box[i]+[conf[i]]+[id[i]] for i in range(len(box)) if i in ind]
    return objects

model,out_layers,class_names=construct_yolo_v3()		# YOLO 모델 생성
colors=np.random.uniform(0,255,size=(len(class_names),3))	# 부류마다 색깔

img=cv.imread(path+'soccer.jpg')
if img is None: sys.exit('파일이 없습니다.')

res=yolo_detect(img,model,out_layers)	# YOLO 모델로 물체 검출

for i in range(len(res)):			# 검출된 물체를 영상에 표시
    x1,y1,x2,y2,confidence,id=res[i]
    text=str(class_names[id])+'%.3f'%confidence
    cv.rectangle(img,(x1,y1),(x2,y2),colors[id],2)
    cv.putText(img,text,(x1,y1+30),cv.FONT_HERSHEY_PLAIN,1.5,colors[id],2)

cv.imshow("Object detection by YOLO v.3",img)

cv.waitKey()
cv.destroyAllWindows()

#week 14_YOLO with camera.py
import numpy as np
import cv2 as cv
import sys

path = 'C:/cv_workspace/data/'
def construct_yolo_v3():
    f=open(path+'coco_names.txt', 'r')
    class_names=[line.strip() for line in f.readlines()]

    model=cv.dnn.readNet(path+'yolov3.weights',path+'yolov3.cfg')
    layer_names=model.getLayerNames()
    out_layers=[layer_names[i-1] for i in model.getUnconnectedOutLayers()]
    
    return model,out_layers,class_names

def yolo_detect(img,yolo_model,out_layers):
    height,width=img.shape[0],img.shape[1]
    test_img=cv.dnn.blobFromImage(img,1.0/256,(448,448),(0,0,0),swapRB=True)
    
    yolo_model.setInput(test_img)
    output3=yolo_model.forward(out_layers)
    
    box,conf,id=[],[],[]		# 박스, 신뢰도, 부류 번호
    for output in output3:
        for vec85 in output:
            scores=vec85[5:]
            class_id=np.argmax(scores)
            confidence=scores[class_id]
            if confidence>0.5:	# 신뢰도가 50% 이상인 경우만 취함
                centerx,centery=int(vec85[0]*width),int(vec85[1]*height)
                w,h=int(vec85[2]*width),int(vec85[3]*height)
                x,y=int(centerx-w/2),int(centery-h/2)
                box.append([x,y,x+w,y+h])
                conf.append(float(confidence))
                id.append(class_id)
            
    ind=cv.dnn.NMSBoxes(box,conf,0.5,0.4)
    objects=[box[i]+[conf[i]]+[id[i]] for i in range(len(box)) if i in ind]
    return objects

model,out_layers,class_names=construct_yolo_v3()		# YOLO 모델 생성
colors=np.random.uniform(0,255,size=(len(class_names),3))	# 부류마다 색깔

cap=cv.VideoCapture(0,cv.CAP_DSHOW)
if not cap.isOpened(): sys.exit('카메라 연결 실패')

while True:
    ret,frame=cap.read()
    if not ret: sys.exit('프레임 획득에 실패하여 루프를 나갑니다.')
        
    res=yolo_detect(frame,model,out_layers)   
 
    for i in range(len(res)):
        x1,y1,x2,y2,confidence,id=res[i]
        text=str(class_names[id])+'%.3f'%confidence
        cv.rectangle(frame,(x1,y1),(x2,y2),colors[id],2)
        cv.putText(frame,text,(x1,y1+30),cv.FONT_HERSHEY_PLAIN,1.5,colors[id],2)
    
    cv.imshow("Object detection from video by YOLO v.3",frame)
    
    key=cv.waitKey(1) 
    if key==ord('q'): break 
    
cap.release()		# 카메라와 연결을 끊음
cv.destroyAllWindows()


