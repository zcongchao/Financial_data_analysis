# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 06:08:02 2018

@author: Administrator
"""
from sklearn import linear_model
import numpy as np

def linear_regression(x_train,x_test,y_train,y_test):
    regr = linear_model.Ridge()
    regr.fit(x_train,y_train)
    
    return regr.score(x_test,y_test), \
            np.mean((regr.predict(x_test)-y_test)**2), \
            regr.coef_,regr.intercept_
            
