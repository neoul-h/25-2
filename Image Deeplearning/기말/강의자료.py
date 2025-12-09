#기말고사 코드 정리

#9주차 – 영상 처리 II
import cv2 as cv
import numpy as np

img = cv.imread('C:/cv_workspace/data/soccer.jpg')
img = cv.resize(img, dsize=(0, 0), fx=0.25, fy=0.25)

def gamma(f, gamma=1.0):
    f1 = f / 255.0
    return np.uint8(255 * (f1 ** gamma))

gc = np.hstack((gamma(img,0.5),gamma(img,0.75),gamma(img,1.0),gamma(img,2.0),gamma(img,3.0)))
cv.imshow('gamma', gc); cv.waitKey(); cv.destroyAllWindows()

import cv2 as cv
import numpy as np

img = cv.imread('C:/cv_workspace/data/soccer.jpg')
img = cv.resize(img, dsize=(0,0), fx=0.4, fy=0.4)
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

femboss = np.array([[-1,0,0],[0,0,0],[0,0,1]])
gray16 = np.int16(gray)
emboss = np.uint8(np.clip(cv.filter2D(gray16,-1,femboss)+128,0,255))

cv.imshow('Emboss', emboss); cv.waitKey(); cv.destroyAllWindows()

import cv2 as cv

img = cv.imread('C:/cv_workspace/data/rose.png')
patch = img[250:350,170:270,:]
patch1 = cv.resize(patch,None,fx=5,fy=5,interpolation=cv.INTER_NEAREST)
patch2 = cv.resize(patch,None,fx=5,fy=5,interpolation=cv.INTER_LINEAR)
patch3 = cv.resize(patch,None,fx=5,fy=5,interpolation=cv.INTER_CUBIC)

cv.imshow('patch1',patch1);cv.imshow('patch2',patch2);cv.imshow('patch3',patch3)
cv.waitKey();cv.destroyAllWindows()

#10주차 – 엣지 & 영역 검출
import cv2 as cv

img=cv.imread('C:/cv_workspace/data/soccer.jpg')
gray=cv.cvtColor(img,cv.COLOR_BGR2GRAY)

sobelx=cv.convertScaleAbs(cv.Sobel(gray,cv.CV_32F,1,0,ksize=3))
sobely=cv.convertScaleAbs(cv.Sobel(gray,cv.CV_32F,0,1,ksize=3))
edge=cv.addWeighted(sobelx,0.5,sobely,0.5,0)

cv.imshow('edge',edge);cv.waitKey();cv.destroyAllWindows()

import cv2 as cv

img=cv.imread('C:/cv_workspace/data/soccer.jpg')
gray=cv.cvtColor(img,cv.COLOR_BGR2GRAY)
canny=cv.Canny(gray,100,200)

cv.imshow('canny',canny);cv.waitKey();cv.destroyAllWindows()

import cv2 as cv

img=cv.imread('C:/cv_workspace/data/apple.jpg')
gray=cv.cvtColor(img,cv.COLOR_BGR2GRAY)

apples=cv.HoughCircles(gray,cv.HOUGH_GRADIENT,1,200,param1=150,param2=20,minRadius=50,maxRadius=120)
for i in apples[0]:
    cv.circle(img,(int(i[0]),int(i[1])),int(i[2]),(255,0,0),2)

cv.imshow('Apple',img);cv.waitKey();cv.destroyAllWindows()

#12주차 – CNN I (Fashion-MNIST)
import keras
from sklearn.model_selection import train_test_split

(train_input, train_target),(test_input,test_target)=keras.datasets.fashion_mnist.load_data()
train_scaled=train_input.reshape(-1,28,28,1)/255.0
train_scaled,val_scaled,train_target,val_target=train_test_split(train_scaled,train_target,test_size=0.2,random_state=42)

model=keras.Sequential([
    keras.layers.Input(shape=(28,28,1)),
    keras.layers.Conv2D(32,3,padding='same',activation='relu'),
    keras.layers.MaxPooling2D(2),
    keras.layers.Conv2D(64,3,padding='same',activation='relu'),
    keras.layers.MaxPooling2D(2),
    keras.layers.Flatten(),
    keras.layers.Dense(100,activation='relu'),
    keras.layers.Dropout(0.4),
    keras.layers.Dense(10,activation='softmax')
])
model.summary()

model.compile(optimizer='adam',loss='sparse_categorical_crossentropy',metrics=['accuracy'])
checkpoint_cb=keras.callbacks.ModelCheckpoint('best-cnn-model.keras',save_best_only=True)
early_stopping_cb=keras.callbacks.EarlyStopping(patience=2,restore_best_weights=True)

#13주차 – CNN II (Optimizer 비교)
from tensorflow.keras.optimizers import SGD
mixed_opt=SGD(learning_rate=0.01,momentum=0.0)
cnn.compile(loss='categorical_crossentropy',optimizer=mixed_opt,metrics=['accuracy'])

from tensorflow.keras.optimizers import Adagrad
ada_opt=Adagrad(learning_rate=0.001)
cnn.compile(loss='categorical_crossentropy',optimizer=ada_opt,metrics=['accuracy'])

from tensorflow.keras.optimizers import RMSprop
rms_opt=RMSprop(learning_rate=0.001,rho=0.9)
cnn.compile(loss='categorical_crossentropy',optimizer=rms_opt,metrics=['accuracy'])

#14주차 – YOLO V3
import numpy as np
import cv2 as cv

def construct_yolo_v3():
    class_names=[c.strip() for c in open('coco.names.txt')]
    model=cv.dnn.readNet('yolov3.weights','yolov3.cfg')
    ln=model.getLayerNames()
    out_layers=[ln[i-1] for i in model.getUnconnectedOutLayers()]
    return model,out_layers,class_names

def yolo_detect(img,model,out_layers):
    H,W=img.shape[:2]
    blob=cv.dnn.blobFromImage(img,1/255,(448,448),(0,0,0),swapRB=True)
    model.setInput(blob)
    outputs=model.forward(out_layers)
    box,conf,ids=[],[],[]
    for out in outputs:
        for det in out:
            scores=det[5:];cid=np.argmax(scores);cf=scores[cid]
            if cf>0.5:
                cx,cy,w,h=det[0:4]*np.array([W,H,W,H])
                box.append([int(cx-w/2),int(cy-h/2),int(w),int(h)])
                conf.append(float(cf));ids.append(int(cid))
    idx=cv.dnn.NMSBoxes(box,conf,0.5,0.4)
    return idx,box,ids,conf
