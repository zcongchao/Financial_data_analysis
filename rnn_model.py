# -*- coding: utf-8 -*-
"""
Created on Sun Mar 11 11:43:36 2018

@author: Administrator
"""

import datetime as dt
from data_preprocess import load_data
from data_preprocess import Extract_Features
from sklearn import preprocessing
from algorithum.reg_lstm import reg_lstm
import numpy as np
import csv
from back_test import estimate
from visualization.plt_show import plt_show
import os
os.environ['THEANO_FLAGS'] = "device=cpu"
import warnings
warnings.filterwarnings("ignore")

path = 'D:/vn.py/vnpy-1.7.1/securities_analysis/data/'
code = '601336'

dates = []
oneDayLine = []
thirtyDayLine = []
month_dates = []

#准备训练数据**************************************************************************************
load_data.download_to_mongodb(code)
oneDayLine, dates = load_data.load_from_mongodb(code,ktype ='D')
dates = [dt.datetime.strptime(d, '%Y-%m-%d').date() for d in dates]

ef = Extract_Features.Extract_Features()
X, y = load_data.To_DL_datatype(code)
X = preprocessing.scale(X)
y = preprocessing.scale(y)
X_train, X_test, Y_train, Y_test = load_data.create_Xt_Yt(X, y, 0.8)
X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))

#训练模型******************************************************************************************
model = reg_lstm(19)
model.fit(X_train,
          Y_train,
          nb_epoch=1,
          batch_size=50,
          verbose=1,
          validation_split=0.1)
score = model.evaluate(X_test, Y_test, batch_size=50)
print score
predicted_Y_test = model.predict(X_test)


with open(path+'predicted_Y_test.csv','wt') as fout:
    csvout = csv.writer(fout)
    csvout.writerows(predicted_Y_test)
        
#计算误差和结果可视化*******************************************************************************
my_rmse = estimate.rmse(predicted_Y_test, Y_test)
print "rmse = ", my_rmse

plt_show(dates,Y_test,predicted_Y_test)