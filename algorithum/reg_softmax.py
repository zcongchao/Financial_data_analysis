# -*- coding: utf-8 -*-
"""
Created on Sun Mar 11 17:41:59 2018

@author: Administrator
"""

import tensorflow as tf
import pandas as pd
import numpy as np
from numpy import *

def softmax_regression(x_train,x_test,y_train,y_test):
    x_train = np.matrix(x_train)
    x_test = np.matrix(x_test)
    y_train = np.matrix(y_train).T
    y_test = np.matrix(y_test).T
    
    n_samples = x_train.shape[0]
    feature_dim = x_train.shape[1]
    
    sess = tf.InteractiveSession()
    
    x = tf.placeholder(tf.float32,[None,feature_dim])
    y = tf.placeholder(tf.float32,[None,1])
    
    w = tf.Variable(tf.zeros([feature_dim,1]))
    b = tf.Variable(tf.zeros([1]))
    
    #softmax regression 算法
    y_ = tf.nn.softmax(tf.matmul(x,w)+b)
    
    
    #y_是真实的label,y是预测的label
    cross_entropy = tf.reduce_mean(-tf.reduce_sum(y*tf.log(y_),reduction_indices=[1]))
    
    #定义优化算法,学习速率0.5，优化目标设定为cross_entropy
    train_step = tf.train.GradientDescentOptimizer(0.5).minimize(cross_entropy)
    #使用全局优化器，执行run方法
    tf.global_variables_initializer().run()
    
    for i in range(1000):
        #batch_xs = x_train.next_batch(100)
        #batch_ys = y_train.next_batch(100)
        train_step.run({x:x_train,y:y_train})
        
    #计算准确率,tf.argmax(y,1)求预测数值中概率最大的那一个序号,tf.argmax(y_,1)找出真实数字类别
    #tf.equal方法判断预测的数字类别是否就是正确的类别
    correct_prediction = tf.equal(tf.argmax(y_,1),tf.argmax(y,1))
    #tf.cast将之前输出的bool值转化为float32,再求平均
    accuracy = tf.reduce_mean(tf.cast(correct_prediction,tf.float32))
    return accuracy.eval({x:x_test,y:y_test})