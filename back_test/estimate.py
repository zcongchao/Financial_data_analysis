# -*- coding: utf-8 -*-
"""
Created on Sun Mar 11 11:43:36 2018

@author: Administrator
"""

import numpy as np
from sklearn.metrics import r2_score
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score

#计算均方根差******************************************************************************************
def rmse(predictions, targets):
    return np.sqrt(((predictions-targets)**2).mean())
    
#计算绝对误差******************************************************************************************
def mae(predictions, targets):
    return np.average(np.abs(predictions - targets),axis=0)
    
#计算r方******************************************************************************************
def R2_score(predictions, targets):
    return r2_score(targets,predictions)
    
#计算分类指标**************************************************************************************
def classify_score(predictions, targets):
    return accuracy_score(targets,predictions), \
            precision_score(targets,predictions), \
            recall_score(targets,predictions), \
            f1_score(targets,predictions)
            
            
    