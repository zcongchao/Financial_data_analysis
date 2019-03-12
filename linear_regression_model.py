# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 06:40:40 2018

@author: Administrator
"""

import datetime as dt
from data_preprocess import load_data
from data_preprocess import Extract_Features
from sklearn import preprocessing
from algorithum.reg_linear import linear_regression
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

#准备训练数据**************************************************************************************
load_data.download_to_mongodb(code)
oneDayLine, dates = load_data.load_from_mongodb(code,ktype ='D')
dates = [dt.datetime.strptime(d, '%Y-%m-%d').date() for d in dates]

ef = Extract_Features.Extract_Features()
X, y = load_data.To_DL_datatype(code)
X = preprocessing.scale(X)
y = preprocessing.scale(y)
X_train, X_test, Y_train, Y_test = load_data.create_Xt_Yt(X, y, 0.8)

#训练模型******************************************************************************************
score,accuracy,coefficients,intercept = linear_regression(X_train, X_test, Y_train, Y_test)

print score