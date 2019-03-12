# -*- coding: utf-8 -*-
"""
Created on Wed Mar 14 07:03:59 2018

@author: Administrator
"""

import matplotlib.pyplot as plt
from data_preprocess.load_data import *
from data_preprocess.Extract_Features import Extract_Features
from sklearn import preprocessing
from algorithum.reg_mlp import dnn_mlp
import warnings

warnings.filterwarnings("ignore")


code = '601336'

ef = Extract_Features()
X, y = To_DL_datatype(code)
X = preprocessing.scale(X)
y = preprocessing.scale(y)
X_train, X_test, Y_train, Y_test = create_Xt_Yt(X, y, 0.8)
#X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
#X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))

accuracy = dnn_mlp(X_train, X_test, Y_train, Y_test)
print accuracy