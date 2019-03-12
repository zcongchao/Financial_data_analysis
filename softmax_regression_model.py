# -*- coding: utf-8 -*-
"""
Created on Sun Mar 11 17:44:57 2018

@author: Administrator
"""

import matplotlib.pyplot as plt
import datetime as dt
from data_preprocess.load_data import *
from data_preprocess.Extract_Features import Extract_Features
from sklearn import preprocessing
from algorithum.reg_softmax import softmax_regression
import warnings
warnings.filterwarnings("ignore")

code = '601336'

ef = Extract_Features()
X, y = To_DL_datatype(code)
X = preprocessing.scale(X)
y = preprocessing.scale(y)
X_train, X_test, Y_train, Y_test = create_Xt_Yt(X, y, 0.8)
X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))

accuracy = softmax_regression(X_train, X_test, Y_train, Y_test)
print accuracy