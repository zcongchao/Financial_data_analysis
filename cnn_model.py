# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 10:44:07 2018

@author: Administrator
"""

#观察数据集
import os
import shutil
import random
from keras.models import Sequential
from keras.layers import Convolution2D,MaxPooling2D
from keras.layers import Activation,Dropout,Flatten,Dense
from data_preprocess import load_data 
from keras.preprocessing.image import ImageDataGenerator
import warnings
warnings.filterwarnings("ignore")

code = '601336'
data_path = 'D:/vn.py/vnpy-1.7.1/securities_analysis/data/'
path = 'D:/vn.py/vnpy-1.7.1/securities_analysis/data/K_img/'
days = 22

if os.path.exists(path+ str(code) + '_qfq.csv') is not True:
    load_data.download_fq_data_from_tushare(code)

if os.path.isdir(path + code +'/') is not True:
    load_data.plot_Kline_imgs_for_X(code,days)
if os.path.isdir(path + code +'/'+'train'+'/') is not True:
    load_data.prepare_Kline_imgs_for_X(code)
    

#预处理样本****************************************************************************************

img_width,img_heigth = 128,128#图片尺寸
input_shape = (img_width,img_heigth,3)

train_data_dir = path + code +'/'+'train'
validation_data_dir = path + code +'/'+ 'validation'

#这里将用一些图片变形手段生成变形图片
train_pic_gen = ImageDataGenerator(
        rescale=1./255,#对输入图片归一化到0-1区间
        rotation_range=20, #随机旋转角度范围
        width_shift_range=0.2, #随机水平移动的范围
        height_shift_range=0.2, #随机垂直移动的范围
        shear_range=0.2, #裁剪程度
        zoom_range=0.5, #随机局部放大的程度
        horizontal_flip=True, #水平翻转
        fill_mode='nearest')#填充新像素的方式

#测试集不做变形处理，只需要做归一化
validation_pic_gen = ImageDataGenerator(rescale=1./255)

#生成数据流，因为这里是二分类问题，标签非0即1，所以不需要进行one-hot编码
#按文件夹生成训练集和标签，binary:二分类
train_flow = train_pic_gen.flow_from_directory(
        train_data_dir,
        target_size = (img_width,img_heigth),
        batch_size = 32,
        class_mode='binary')
#按文件夹生成测试集和标签
validation_flow = validation_pic_gen.flow_from_directory(
        validation_data_dir,
        target_size=(img_width,img_heigth),
        batch_size=32,
        class_mode='binary')
        
#训练模型****************************************************************************


nb_train_samples = 2000
nb_validation_samples = 1000
nb_epoch = 2 #循环50轮

#两层卷积-池化，提取64个平面特征
model = Sequential([Convolution2D(32,3,3,input_shape=input_shape,activation='relu'),
                   MaxPooling2D(pool_size=(2,2)),
                   Convolution2D(64,3,3,activation='relu'),
                   MaxPooling2D(pool_size=(2,2)),
                   Flatten(),
                   Dense(64,activation='relu'),
                   Dropout(0.5),
                   Dense(1,activation='sigmoid'),
                   ])

#损失函数设置为二分类交叉熵
model.compile(loss='binary_crossentropy',
             optimizer = 'rmsprop',
             metrics=['accuracy'])
             
model.fit_generator(
    train_flow,
    samples_per_epoch = nb_train_samples,
    nb_epoch=nb_epoch,
    validation_data=validation_flow,
    nb_val_samples=nb_validation_samples)
    
#保存训练结果********************************************************************************
def ensure_dir(dir_path):
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
        except OSError:
            pass

ensure_dir(path + code +'/'+'weights')
model.save_weights(path + code +'/'+'weights/' + '1.h5')